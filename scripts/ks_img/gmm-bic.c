#include <stdio.h>
#include <string.h>
#include <math.h>

#define MAX_SEGMENTS 40

/* Check sd as follows
gcc gmm-bic.c -lm -o gmm-bic
gmm-bic 3 749 oil.dat

Segment,    Mu,    Orig-Mu,        SD,   Mix.Prob.     Card.
1 , 21.003319 , 17.599658 , 6.629804, 0.119210,  105
2 , 78.266766 , 19.807108 , 33.210456, 0.679207,  502
3 , 190.457096 , 24.131935 , 32.736168, 0.201583,  142

In S-Plus (oil.dat = input data, yyyy = cut and paste of 
cluster assignments from standard output device):
a <- scan('oil.dat')
yyyy <- scan('yyyy')
(Labels in yyyy)
mean(a[yyyy==1])
17.58229
mean(a[yyyy==2])
19.92508
mean(a[yyyy==3])
24.34845
sqrt(var(a[yyyy==1]))
0.2079167
sqrt(var(a[yyyy==2]))
1.21213
sqrt(var(a[yyyy==3]))
1.069975

For BIC:
1  -8282
2  -8150
3  -8097   <---  
4  -8101
5  -8118
6  -8136

*/


/* ************************************************************
   gmm-bic.c
   Mixture model fitting, for a given number of Gaussian clusters.
   Output including BIC value to standard output. 
   Algorithm: determine a 256-length histogram of input data.
   Use EM (expectation-maximization) to find MLE solution 
   (maximum likelihood estimators of mixture model parameters).

   Usage
   gcc gmm-bic.c -lm -o gmm-bic
   gcc-bic                   [writes out syntax]
   gmm-bic 4 749 oil.dat  

   FM, 2003/4
   ******************************************************************* */

main(argc, argv)
     int argc;
     char *argv[];

{                     
  FILE *stream; 
  void  free_vector(), erhand();
  float Normi(), Normr(), *in_vector, *vector(), *labs, datamin, datamax;
  float *orig_vector, p, pmax, ival, mlikedenom, in_value;
  double mu[MAX_SEGMENTS], sd[MAX_SEGMENTS];
  double loglik_old, loglik_new, conv_crit, segment_probs[MAX_SEGMENTS];
  double dsegment_number, segment_probs_total, denom[256];
  double mu_numer, mu_denom, sd_numer, sd_denom, loglik_sum;
  double dnorm_lookup[256][MAX_SEGMENTS], delta_lookup[256][MAX_SEGMENTS];
  int i, j, k, iseg, segment_number, n;
  int iter_counter, max_iterations, current_breakpoint, current_total, done;
  int greyscale_histogram[256], initial_breakpoints[(MAX_SEGMENTS+1)];
  int sd_counter[MAX_SEGMENTS], mu_counter[MAX_SEGMENTS];
  int empty_levels, initialization_multiplier, initialization_error;
  int cardinality[MAX_SEGMENTS];

  if (argc != 4)
    {
      printf("Syntax: gmm-bic no_of_clusters no_of_vals input_file\n");
      printf("Max no. of clusters currently supported: 40\n");
      exit(1);
    }

  segment_number     = atoi(argv[1]); 
  printf("Number of clusters wanted: %d.\n",segment_number);

  n = atoi(argv[2]);     
  printf("Number of input data values: %d.\n",n); 

  if ((stream = fopen(argv[3],"r")) == NULL)  {
     fprintf(stderr, "Program %s : cannot open file %s\n",
                       argv[0], argv[3]);
     fprintf(stderr, "Exiting to system.");
     exit(1);
  }

  orig_vector = vector(0,n-1); /* Input data */
  in_vector = vector(0,n-1); /* Input data */
  labs = vector(0,n-1);      /* Used later for cluster labels */
  for (i = 0; i < n; i++)  {
      fscanf(stream, "%f", &in_value);
      orig_vector[i] = in_value;
  }

  printf("Check on first 10 values of input data:\n");
  for (i = 0; i < 10; i++) printf("%5.1f", orig_vector[i]);  

  /* Transform data */
  /*
  for (i = 0; i < n-1; i++) 
        in_vector[i] = log(orig_vector[i+1])-log(orig_vector[i]);
  */
  /*  in_vector[i] = log(orig_vector[i+1] - orig_vector[i]); */
  /* n = n - 1; */    /* One value less if we are working on differences */
  for (i = 0; i < n; i++) in_vector[i] = orig_vector[i];

  datamin  = 1.0E30;
  datamax  = -1.0E30;
  for (i = 0; i < n; i++)  {
      if (in_vector[i] < datamin) datamin = in_vector[i];
      if (in_vector[i] > datamax) datamax = in_vector[i];
  }
  printf("\nMin and max values =  %f, %f\n", datamin, datamax);


   /* delta_lookup is prob of a datum (we're using histogram) with
   value j being in segment i.
   mu, sd, and segment_probs are the estimated mean, standard deviation, 
   and mixture probability for each segment. */

   loglik_old      = 0;              /* Some initializations */
   loglik_new      = 1;
   max_iterations  = 200;
   dsegment_number = segment_number; /* explicit type conversion */
   for (i=0; i<segment_number; i++) {
       mu[i]            = 0.0;
       sd[i]            = 0.0;
       mu_counter[i]    = 0;
       sd_counter[i]    = 0;
       segment_probs[i] = (1.0/dsegment_number);
   }                                                 

   /* Rescale values to 0..255 */
   for (i = 0; i < n; i++) 
       in_vector[i] = 255.0*(in_vector[i]-datamin)/(datamax-datamin);

   /* Initialize delta_lookup to the starting guess 
      the starting guess is found by dividing the histogram of greyscale 
      levels into equally sized pieces, so initially each segment will 
      have the same segment probability.*/

   /* Find cardinality of each greyscale level (histogram bin card.) */
   empty_levels=0;

   for (i=0; i<256; i++) {
       greyscale_histogram[i] = 0;
       for (j=0; j<n; j++) {
           if ((int)in_vector[j]==i) greyscale_histogram[i] += 1; 
       }
   if (greyscale_histogram[i]==0) empty_levels+=1;
   }

   printf("Greyscale histogram follows, 256 values.\n");
   for (i=0; i<256; i++) printf("%d ",greyscale_histogram[i]);
   printf("\n");

   /* For the initial segmentation, there are a total of n values to be 
      divided (roughly) equally among number_segment initial segments. 
      Thus we want about n/number_segment values in each bin.  We use
      initial_breakpoints to store the breakpoints of our binning. 

      Note that this will not give a good result when all the points 
      are in one histogram bin.  Warning: problems if hist. sparse! 

      We should check to make sure the number of unique non-zero grey 
      levels (or non-empty histogram bins) is larger than segment_number.  
      If not, this should fail gracefully.  */ 

   initial_breakpoints[0]              = -1; 
   initial_breakpoints[segment_number] = 256;
   current_breakpoint                  = -1;
   initialization_error                = 0;

   for (i=1; i<(segment_number); i++) {
       current_total = 0;
       done = 0;
       while (done==0) {
             current_breakpoint += 1;
             if (current_breakpoint==255) initialization_error+=1;
             current_total += greyscale_histogram[current_breakpoint];
             if (current_total >= (n/segment_number) ) {
                initial_breakpoints[i] = current_breakpoint;
                done = 1;
             }
       }
       if (current_total==0) initialization_error+=1;
   }

   initialization_multiplier = 1;           
   while (initialization_error > 0) {

         initial_breakpoints[0]              = -1;
         initial_breakpoints[segment_number] = 256;
         current_breakpoint                  = -1;
         initialization_error                = 0;
         initialization_multiplier           = initialization_multiplier*2;

         for (i=1; i<(segment_number); i++) {
             current_total = 0;
             done = 0;
             while (done==0) {
                   current_breakpoint += 1;
                   if (current_breakpoint==255) initialization_error+=1;
                   current_total += greyscale_histogram[current_breakpoint];

                   if (initialization_multiplier == 0) {
                      printf("Pathological case in histogram. Stopping.\n");
                      exit(1);
                   }
                   if (initialization_multiplier >= 4096) {
                      printf("Pathological case in histogram. Stopping.\n");
                      exit(1);
		   }

                   if (current_total >= (int)((float)n/
                   ( (float)initialization_multiplier *
                     (float)segment_number ))) {
                      initial_breakpoints[i] = current_breakpoint;
                      done = 1;
		   }
	     }
             if (current_total==0) initialization_error+=1;
	 }
   }                                            

   /* Check here that the init breaks are valid.  If not, probably trying
      to fit more segments than unique greyscale values (or non-zero
      histogram bins). */

   for (i=0; i<(segment_number); i++) {
       for (j=0; j<256; j++) {
           if ( (j>initial_breakpoints[i]) &&
                (j<= initial_breakpoints[(i+1)])) {
              delta_lookup[j][i] = 1.0; }
           else delta_lookup[j][i] = 0.0;
       }
   }

   /* End of initializing delta_lookup*/

   /* Initialize mu to the starting guess */
   for (i=0; i<segment_number; i++) {
        for (j=0; j<256; j++) {                      
            if (delta_lookup[j][i] == 1.0) {
               mu[i] += (double)j*(double)greyscale_histogram[j];
               mu_counter[i] += greyscale_histogram[j];
            }
        }
   }

   for (i=0; i<segment_number; i++) {
       if (mu_counter[i] == 0) {
          printf("BIC: -99999900.0\n");
          erhand("Cluster empty. BIC: NA");
       }
       mu[i] = (mu[i]/(double)mu_counter[i]);
   }

   /* Initialize sd to the starting guess */
   for (i=0; i<segment_number; i++) {
       for (j=0; j<256; j++) {
           if (delta_lookup[j][i] == 1.0) {
	      sd[i] += (double)greyscale_histogram[j]*
			     pow(((double)j-mu[i]),2);  
              sd_counter[i] += greyscale_histogram[j];
           }
       }
   }

   for (i=0; i<segment_number; i++) {
       sd[i] = sqrt(sd[i]/((double)sd_counter[i] - 1.0));
       /* Avoid zero std. dev. by giving instead a small value. */
       if (sd[i]==0.0) sd[i] = .25;
   }

  /* Use EM algorithm to find MLE for segment_number segments.
     Note that the first step will have a negative change in 
     loglikelihood since the first loglik_old value is zero. */
  iter_counter = 0;

  /* Set the convergence criterion based on the number of observations.
     We want the average change in loglikelihood per val. to be less than
     .00001, so we multiply the number of values by .00001 to get the
     convergence criterion (with an upper bound of 1). */
  conv_crit = (double)n*(0.00001);
  if (conv_crit>1.0) conv_crit=1.0;
  printf("Convergence criterion  %f \n",conv_crit);
 
  /* Main while loop ************* */
  while ( (fabs(loglik_new-loglik_old) > (float)conv_crit) ||
         (iter_counter==0) ) {

        iter_counter += 1;
        /* E-step */

        /* Only need to calculate the Gaussian probs. for values 0-255 
           for each segment*/
        for (i=0; i<segment_number; i++) {
            for (j=0; j<256; j++)
                dnorm_lookup[j][i] = segment_probs[i] *Normi(j,mu[i],sd[i]);
        }

        for (j=0; j<256; j++) denom[j] = 0.0;

        for (i=0; i<segment_number; i++) {
            for (j=0; j<256; j++) denom[j] = denom[j] + (dnorm_lookup[j][i]);
        }

        /* if denom[j]=0, then there are no points with greyscale level j, 
        so delta_lookup will never be called for that value of j unless 
        multiplied by greyscale histogram[j] which will be zero. */
        for (i=0; i<segment_number; i++) {
            for (j=0; j<256; j++) {
                if (denom[j]>0)
                   delta_lookup[j][i] = dnorm_lookup[j][i]/denom[j];
                else delta_lookup[j][i] = 0;
            }
        }

        /* M-step */

        if (fmod(iter_counter,1000)==0) 
           printf("Another 1000 iterations...\n");

        /* update segment_probs */               
        for (i=0; i<segment_number; i++) segment_probs[i] = 0.0;

        for (i=0; i<segment_number; i++) {
            for (j=0; j<256; j++) 
                segment_probs[i]+=(delta_lookup[j][i])*greyscale_histogram[j];
        }

        for (i=0; i<segment_number; i++) 
            segment_probs[i] = segment_probs[i]/(float)n;

        segment_probs_total = 0.0;
        for (i=0; i<segment_number; i++) 
            segment_probs_total += segment_probs[i]; 

        for (i=0; i<segment_number; i++)
         segment_probs[i] = segment_probs[i]/segment_probs_total;
                              
        /* Update mu */

        for (i=0; i<segment_number; i++) {
            mu_numer = 0.0;
            mu_denom = 0.0;

            for (j=0; j<256; j++) {
                mu_numer += (delta_lookup[j][i])*(j*greyscale_histogram[j]);
                mu_denom += (delta_lookup[j][i])*greyscale_histogram[j];
            }

            mu[i] = mu_numer/mu_denom;
	}

        /* Update sd */

        for (i=0; i<segment_number; i++) {
            sd_numer = 0.0;
            sd_denom = 0.0;

            for (j=0; j<256; j++) {
	        sd_numer += greyscale_histogram[j]*
				pow((j-mu[i]),2)*delta_lookup[j][i]; 
                sd_denom += greyscale_histogram[j]*delta_lookup[j][i];
            }

            sd[i] = sqrt(sd_numer/sd_denom);
            /* We know that the resolution of our values cannot be 
               better than 1 greyscale level, so sd should not fall 
               below 1/4. */
            if (sd[i]<.25) { sd[i] = .25; }
	}

        /* Segment probs have been updated, so now update dnorm_lookup*/
        for (i=0; i<segment_number; i++) {
            for (j=0; j<256; j++) 
                dnorm_lookup[j][i] = segment_probs[i] *Normi(j,mu[i],sd[i]);
        }

        /* Update likelihood */

        loglik_old = loglik_new;
        loglik_new = 0.0;

        for (j=0; j<256; j++) {
            loglik_sum = 0.0;
            for (i=0; i<segment_number; i++) 
                loglik_sum += dnorm_lookup[j][i];
            if (loglik_sum>0) loglik_new += 
                greyscale_histogram[j]*log(loglik_sum);
            /* Otherwise, greyscale_histogram will be zero, so add zero. */
	}

        /*
        printf("Loglikelihood: %24f \n",loglik_new);
        printf("Change: %24f \n",(loglik_new-loglik_old));
        printf("BIC: %14f \n",(2*loglik_new-((3*segment_number)-1)*log(w*h)));
        */    

  } /* End of while loop.  EM has converged (or diverged beyond precision)*/


  /* Classify each pixel into its most likely segment */

  printf("\n");
  printf("Loglikelihood: %24f \n",loglik_new);
  /* printf("Change: %24f \n",(loglik_new-loglik_old)); */
  printf("BIC: %14.0f         No.clusters: %d \n",
    (2*loglik_new - ((3*segment_number)-1)*log((float)n)), segment_number);
  printf("\n");

  printf("Now determining posteriors, for each pixel.\n");
  /* Determine posteriors.  By Bayes:
     prob(seg-k | ival) = f(ival | seg-k) . prob(seg-k) /
                     sum_r f(ival | seg-r) . prob(seg-r) 
     where LHS is posterior probability of seg-k given the data, ival,
     f(ival | seg-k) is the integrated or marginal likelihood of seg k
     prob(seg-k) is prior probability */

  for (k = 0; k < segment_number; k++) cardinality[k] = 0;

  for (i=0; i < n; i++) {
      labs[i] = 0; 
      ival = in_vector[i];
      pmax = 0.0;
      iseg = 0;
      mlikedenom = 0.0;
      for (k=0; k<segment_number; k++)
           mlikedenom += Normr(ival, mu[k], sd[k]) * segment_probs[k];
      for (k=0; k<segment_number; k++) {
          p = (Normr(ival, mu[k], sd[k]) * segment_probs[k])/mlikedenom;
          if (p > pmax) {
	     pmax = p;
             iseg = k;
          }
      }
      /* Increment cluster numbers by one so sequence is 1, 2, ... */
      labs[i] = iseg + 1;
      cardinality[iseg] += 1;
  }

  /* For convenience, redo stdevs from original data */
  for (j=0; j<segment_number; j++) {
      /* Use p for convenience as rectified mean */
      p = ((float)mu[j]*(datamax-datamin)/255.0)+datamin;
      sd[j] = 0.0; 
      for (i=0; i< n; i++) {
	  if (labs[i] == j+1) {
             ival = (in_vector[i]*(datamax-datamin)/255.0)+datamin;
             sd[j] += pow(ival-p,2);
	  }
      }
      sd[j] = sqrt(sd[j]/(float)cardinality[j]); 
  }
  
  printf("Labels are 1, 2, ... no. clusters.\n"); 
  printf("Segment,  Mu,       SD, Mix.Prob, Card.\n");
  for (i=0; i<segment_number; i++) {
      printf("%i, %f, %f, %f,  %d\n",i+1,
      (mu[i]*(datamax-datamin)/255.0)+datamin,sd[i],segment_probs[i],
      cardinality[i]);
  }

   printf("Labels follow, n values.\n");
   for (i=0; i<n; i++) printf("%.0f ",labs[i]);
   printf("\n");

  free_vector(in_vector, 0, n-1); 
  free_vector(labs, 0, n-1); 
  printf("Finished.\n");

}

      /* Error handler */
      void erhand(err_msg)    
      char err_msg[];
      /* Error handler */
      {
         fprintf(stderr,"Run-time error:  ");
         fprintf(stderr,"%s   ", err_msg);
         fprintf(stderr,"Exiting to system.\n");
         exit(1);
      }
                                         

      /* Allocation of vector storage */
      float *vector(n0, n)
      int n0, n;
      /* Allocates a float vector with range [n0..n]. */
      {
         float *v;
         v = (float *) malloc ((unsigned) (n-n0+1)*sizeof(float));
         if (!v) erhand("Allocation failure in vector().");
         return v-n0;                                             
      }


      /* Deallocate vector storage */
      void free_vector(v,n0,n)
      float *v;
      int n0, n;
      /* Free a float vector allocated by vector(). */
      {
         free((char*) (v+n0));
      }


      extern float Normi(x,mu,sd)
      int x;
      float mu,sd;
      {
	 /* Used to compute the Gaussian prob. of integer x. */
         float result,temp;                      
         temp = (float)x-mu;
         result = (1.0/(sd*sqrt(2*3.141593)))*
                     exp(- pow(temp,2)/(2*pow(sd,2)));
         return(result);
      }


      extern float Normr(x,mu,sd)
      float x, mu, sd;
      {
         /* Used to compute the Gaussian probability of real x. */
         float result, temp;                      
         temp = x-mu;
         result = (1.0/(sd*sqrt(2.0*3.141593)))*
                      exp(- pow(temp,2)/(2*pow(sd,2)));
         return(result);
      }
     







