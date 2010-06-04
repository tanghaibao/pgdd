$(function () {
        var icons = {header: "ui-icon-circle-arrow-e", headerSelected:"ui-icon-circle-arrow-s"};
        $("#methods").accordion({icons: icons});
        });
function factdivdiv( n, k1, k2 ) {
   // computes (n! / k1! k2!) for combinations
   // assure k1 >= k2
   if (k1 < k2) { i = k1;  k1 = k2;  k2 = i; }
   if (k1 > n)  t = 0;
   else {
      // accumulate the factors for k2 factorial
      var t=1;
      while (k2 > 1)
         t *= k2--;
      // accumulate the factors from n downto k1
      var t2=1;
      while (n > k1)
         t2 *= n--;

      t = t2 / t;
      }
   return t;
}
function Comb( n, r ) {
   if ((r == 0) || (r == n))  return 1;
   else
      if ((r > n) || (r < 0))  return 0;
      else
         return  factdivdiv( n, r, n-r );
}
function ex()
{
    $("#K").val("3");
    $("#N").val("30000");
    $("#J1").val("5");
    $("#J2").val("5");
    calc();
}
function calc()
{
    var K = $("#K").val();
    var N = $("#N").val();
    var J1 = $("#J1").val();
    var J2 = $("#J2").val();
    var L1, L2, i;
    L1 = L2 = 0;
    for (i=K-2;i<=J1-2;i++) L1+=Comb(i,K-2);
    for (i=K-2;i<=J2-2;i++) L2+=Comb(i,K-2);
    var ans = 2*L1*L2/Math.pow(N,K-2);
    ans = ans.toPrecision(3);
    $("#display").html("<b><i>Expected occurences of a duplicated set of "+K+" genes occur across a spread of "+J1+" positions in location A and "+J2+" positions in location B, is "+ans+"</i></b>");
    $("#display").show("slow");
}
