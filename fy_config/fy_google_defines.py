# Google related which is used for trade.fyers.in
GOOGLE_ANALYTICS_SCRIPT_1		= """
							<script>
					          (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
					          (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
					          m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
					          })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');

					          ga('create', 'UA-70168752-5', 'auto');
					          ga('send', 'pageview');
					        </script>
							"""
GOOGLE_ANALYTICS_TAG_HEAD_1	= """
							<!-- Google Tag Manager -->
							<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
							new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
							j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
							'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
							})(window,document,'script','dataLayer','GTM-P9DMNS7');</script>
							<!-- End Google Tag Manager -->
							"""
GOOGLE_ANALYTICS_TAG_BODY_1	="""
						<!-- Google Tag Manager (noscript) -->
						<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-P9DMNS7"
						height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
						<!-- End Google Tag Manager (noscript) -->
						"""
GOOGLE_ANALYTICS_JQ_GTM_1			= ""

# This should be in the first line of html <head> tag
GOOGLE_ANALYTICS_GLOBAL_SITE_TAG = """
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-70168752-5"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'UA-70168752-5');
</script>
"""