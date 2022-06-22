from fy_google_defines import *
# Callback related
CALLBACK_DEFAULT_1 = "https://trade.fyers.in"
LOGIN_PAGE_URL_1 = "https://login.fyers.in"
LOGIN_PAGE_CHANGE_PWD_PATH_1 = "/change"

# Codes
LOGIN_PAGE_C_UNLOCK = ""


def generateHtml_loginPage(callBackUrl="", statusMessage="",
                           gaTagHead="", gaTagBody="", gaScript=""):
    loginHtml = """
<html>
    <head>
        %s
        %s
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>FYERS Login</title>
        <link rel="apple-touch-icon" sizes="57x57" href="https://clib.fyers.in/fyers_logos/1/apple-icon-57x57.png">
        <link rel="apple-touch-icon" sizes="60x60" href="https://clib.fyers.in/fyers_logos/1/apple-icon-60x60.png">
        <link rel="apple-touch-icon" sizes="72x72" href="https://clib.fyers.in/fyers_logos/1/apple-icon-72x72.png">
        <link rel="apple-touch-icon" sizes="76x76" href="https://clib.fyers.in/fyers_logos/1/apple-icon-76x76.png">
        <link rel="apple-touch-icon" sizes="114x114" href="https://clib.fyers.in/fyers_logos/1/apple-icon-114x114.png">
        <link rel="apple-touch-icon" sizes="120x120" href="https://clib.fyers.in/fyers_logos/1/apple-icon-120x120.png">
        <link rel="apple-touch-icon" sizes="144x144" href="https://clib.fyers.in/fyers_logos/1/apple-icon-144x144.png">
        <link rel="apple-touch-icon" sizes="152x152" href="https://clib.fyers.in/fyers_logos/1/apple-icon-152x152.png">
        <link rel="apple-touch-icon" sizes="180x180" href="https://clib.fyers.in/fyers_logos/1/apple-icon-180x180.png">
        <link rel="icon" type="image/png" sizes="192x192"  href="https://clib.fyers.in/fyers_logos/1/android-icon-192x192.png">
        <link rel="icon" type="image/png" sizes="16x16" href="https://clib.fyers.in/fyers_logos/1/favicon-16x16.png">
        <link rel="icon" type="image/png" sizes="32x32" href="https://clib.fyers.in/fyers_logos/1/favicon-32x32.png">
        <link rel="icon" type="image/png" sizes="96x96" href="https://clib.fyers.in/fyers_logos/1/favicon-96x96.png">
        <link rel="manifest" href="https://clib.fyers.in/fyers_logos/monochrome/manifest.json">
        <meta name="msapplication-TileColor" content="#ffffff">
        <meta name="msapplication-TileImage" content="https://clib.fyers.in/fyers_logos/1/ms-icon-144x144.png">
        
        <link rel="stylesheet" type="text/css" href="https://clib.fyers.in/lib/bootstrap/3.3.7/bootstrap.min.css">
        <link rel="stylesheet" href="https://clib.fyers.in/lib/animate/3.5.2/animate.min.css">
        <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js"></script>
        <script>
            // Redundancy
           window.jQuery || document.write('<script src="https://clib.fyers.in/lib/jquery/1.12.4/jquery.min.js"><\/script>');
        </script>
        <script type="text/javascript" src="https://clib.fyers.in/lib/bootstrap/3.3.7/bootstrap.min.js"></script> 
        <link href='https://fonts.googleapis.com/css?family=Work+Sans:400,300,700' rel='stylesheet' type='text/css'>
        <script async src="https://www.google-analytics.com/analytics.js"></script>
        <link rel="stylesheet" href="https://clib.fyers.in/styles/fy_login.css">
        %s
    </head>

    <body style="font-family:Calibri;">
        %s
        <div class="container col-md-4 " style="min-width: 300px;">
          <div class="row">
            <div id="newmsg" class="profile profile--open">
            <div class="profile__form" id="loginform">
                <div class="profile__fields">
                    <h3>Login To Your FYERS Account</h3>
                <hr>
                <h5>%s</h5>

                <form method="POST" action="./" id="fy_login">     
                    <input type="hidden" id="cb" name="cb" value="%s" />
                    <input type="hidden" id="typeFlag" name="typeFlag" value="4" />
                    <div class="field">
                        <input type="text" class="form-control" name="fyers_id" placeholder="Client ID (Example: FX0001)" id="fyers_id" style="height: 40px;" required="required"  pattern ="(^[a-zA-Z]{2}[0-9]{3,5}$)" />
                    </div>
                    <div class="field">
                        <input type="password" class="form-control" name="fy_pwd1" placeholder="Password" id="fy_pwd1" style="height: 40px;" required="required" />
                    </div>
                    <div class="field">
                        <input type="text" class="form-control" name="fy_pwd2" placeholder="DOB (Example: 01-01-1990) or PAN no. (Example: ABCDE1234F)" id="fy_pwd2" style="height: 40px;" required="required" pattern ="((^[0-3]?[0-9]-[0-3]?[0-9]-(?:[0-9]{2})?[0-9]{2}$)|(^[A-Za-z]{5}[0-9]{4}[A-Za-z]{1}$))" />
                    </div>

                    <button type="submit" class="btn" value="submit" id="submit">Log In</button>
                    </form>
              <div class="profile__footer">
                  <a href="" id="unblockuser">Unlock Account</a><br>
                  <a href="" id="passchange">Change Password</a><br>
                  <a href="" id="reset">Forgot Password</a><br>
                  <h4><a href="https://www.fyers.in/join-us/" id="join">Open a trading account for free!</a></h4>
              </div>
            </div>
          </div>

          <div class="profile__form hidden" id="unblock">
          <div class="profile__fields">
              <h3>Unlock Yours FYERS Account</h3>
              <hr>
              <h5>%s</h5>

              <form method="POST" action="./" id="RegisterNewUser" >
                <input type="hidden" id="cb" name="cb" value="%s" />
                <input type="hidden" id="typeFlag" name="typeFlag" value="1" />
                <div class="field">
                  <input type="text" class="form-control" name="fyers_id" placeholder="Client ID (Example: FX0001)" id="fyers_id"    style="height: 40px;" required="required"  pattern ="(^[a-zA-Z]{2}[0-9]{3,5}$)" />
                </div>
                <div class="field">
                  <input type="text" class="form-control" name="email" placeholder="Email (Example: abc@xyz.com)" id="email" style="height: 40px;" required="required" />
                </div>
                <div class="field">
                  <input type="text" class="form-control" name="pan" placeholder="PAN No. (Example: ABCDE1234F)" id="pan" style="height: 40px;" required="required" pattern="(^[A-Za-z]{5}[0-9]{4}[A-Za-z]{1}$)" />
                </div>
                <button type="submit" class="btn" value="submit" id="submit" >submit</button>
              </form>
              <div class="profile__footer">
                <a href="" id="login">Log In </a><br>
                <a href="" id="pass">Change Password</a><br>
                <a href="" id="resetpas">Forgot Password</a><br>
                <h4><a href="https://www.fyers.in/join-us/" id="join">Open a trading account for free!</a></h4>
              </div>
            </div>
          </div>

          <div class="profile__form hidden" id="changepass">
            <div class="profile__fields">
              <h3>Change Your FYERS Password</h3>
              <hr>
              <h5>%s</h5>

              <form method="POST" action="./" id="RegisterNewUser" >
                <input type="hidden" id="cb" name="cb" value="%s" />
                <input type="hidden" id="typeFlag" name="typeFlag" value="3" />
                <div class="field">
                  <input type="text" class="form-control" name="fyers_id" placeholder="Client ID (Example: FX0001)" id="fyers_id"    style="height: 40px;" required="required"  pattern ="(^[a-zA-Z]{2}[0-9]{3,5}$)"/>
                </div>
                <div class="field">
                  <input type="password" class="form-control" name="existPwd" placeholder="Existing Password" id="existPwd"   style="height: 40px;" required="required">
                </div>
                <div class="field">
                  <input type="password" class="form-control" name="newChangePwd" placeholder="New Password" id="newChangePwd"   style="height: 40px;" required="required">
                </div>
                <div class="field">
                  <input type="password" class="form-control" name="confirmpwd" placeholder="Confirm New Password" id="confirmpwd"   style="height: 40px;" required="required">
                </div>
                <div class="field">
                  <h4>Password Policy:</h4>
                  <span>&nbsp;1.Password Length:Minimum 6 and Maximum 12</span></br>
                  <span>&nbsp;2.Atleast 1 alphabet and 1 numerical</span><br>
                  <span>&nbsp;3.Atleast 1 of the following special character(! or @ or #)</span>
                </div>

                <button type="submit" name = "submitrp" class="btn" id="submitrp" >submit</button>
              </form>
              <div class="profile__footer">
                <a href="" id="log">Log In</a><br>
                <a href="" id="lock">Unlock Account</a><br>
                <a href="" id="resetpswd">Forgot Password</a><br>
                <h4><a href="https://www.fyers.in/join-us/" id="join">Open a trading account for free!</a></h4>
              </div>
            </div>
          </div>

        <div class="profile__form hidden" id="resetpass">
        <div class="profile__fields">
              <h3>Reset Your FYERS Password</h3>
              <hr>
              <h5>%s</h5>

              <form method="POST" action="./" id="RegisterNewUser" >
                <input type="hidden" id="cb" name="cb" value="%s" />
                <input type="hidden" id="typeFlag" name="typeFlag" value="2" />
                <div class="field">
                  <input type="text" class="form-control" name="fyers_id" placeholder="Client ID (Example: FX0001)" id="fyers_id"    style="height: 40px;" required="required"  pattern ="(^[a-zA-Z]{2}[0-9]{3,5}$)" />
                </div>
                <div class="field">
                  <input type="text" class="form-control" name="email" placeholder="Email (Example: abc@xyz.com)" id="email" style="height: 40px;" required="required" />
                </div>
                <div class="field">
                  <input type="text" class="form-control" name="pan" placeholder="PAN No. (Example: ABCDE1234F)" id="pan" style="height: 40px;" required="required" pattern="(^[A-Za-z]{5}[0-9]{4}[A-Za-z]{1}$)" />
                </div>
                <button type="submit" name = "submit" class="btn" id="submit" >Reset</button>
              </form>
              <div class="profile__footer">
                <a href="" id="loginto">Log In</a><br>
                      <a href="" id="lockusr">Unlock Account</a><br>
                      <a href="" id="passusr">Change Password</a><br>
                      <h4><a href="https://www.fyers.in/join-us/" id="join">Open a trading account for free!</a></h4>
              </div>
            </div>
          </div>
          </div>
          </div>
        </div>

        <script type="text/javascript">

            $(document).ready(function() {
                $("#unblockuser").click(function() {
                    $('#unblock').removeClass('hidden');
                    $('#loginform').addClass('hidden');
                });
                $("#passchange").click(function() {
                    $('#changepass').removeClass('hidden');
                    $('#loginform').addClass('hidden');
                });
                $("#login").click(function() {
                    $('#loginform').removeClass('hidden');
                    $('#unblock').addClass('hidden');
                });
                $("#pass").click(function() {
                    $('#changepass').removeClass('hidden');
                    $('#unblock').addClass('hidden');
                });

                $("#resetpas").click(function() {
                    $('#resetpass').removeClass('hidden');
                    $('#unblock').addClass('hidden');
                });

                $("#log").click(function() {
                    $('#loginform').removeClass('hidden');
                    $('#changepass').addClass('hidden');
                });
                $("#lock").click(function() {
                    $('#changepass').addClass('hidden');
                    $('#unblock').removeClass('hidden');
                });
                $("#resetpswd").click(function() {
                    $('#changepass').addClass('hidden');
                    $('#resetpass').removeClass('hidden');
                });
                $("#reset").click(function() {
                    $('#resetpass').removeClass('hidden');
                    $('#loginform').addClass('hidden');
                });
                $("#loginto").click(function() {
                    $('#resetpass').addClass('hidden');
                    $('#loginform').removeClass('hidden');
                });
                $("#lockusr").click(function() {
                    $('#resetpass').addClass('hidden');
                    $('#unblock').removeClass('hidden');
                });
                $("#passusr").click(function() {
                    $('#resetpass').addClass('hidden');
                    $('#changepass').removeClass('hidden');
                });
                $("#submitrp").click(function () {
                    var password = $("#newChangePwd").val();
                    var confirmPassword = $("#confirmpwd").val();
                    if (password != confirmPassword) {
                        alert("Passwords do not match.");
                        return false;
                    }
                    return true;
                });
            });

            jQuery(function($) {
                $('#unblockuser,#passchange,#login,#pass,#log,#lock,#reset,#loginto,#resetpas,#resetpswd,#lockusr,#passusr').click(function() {
                    return false;
                }).dblclick(function() {
                    window.location = this.href;
                    return false;
                });
            });

        </script>
    </body>
</html>
        """ % (
        GOOGLE_ANALYTICS_GLOBAL_SITE_TAG,gaTagHead, gaTagBody, gaScript, statusMessage, callBackUrl, statusMessage, callBackUrl, statusMessage,
        callBackUrl,
        statusMessage, callBackUrl)
    return loginHtml


def generateHtml_changePasswordPage(callbackUrl="", fyers_id="", errorMessage="",
                                    gaTagHead="", gaTagBody="", gaScript=""):
    changePasswordHtmlVariable = """
<html>
    <head>
        %s
        %s
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>FYERS Change Password</title>
        <link rel="apple-touch-icon" sizes="57x57" href="https://clib.fyers.in/fyers_logos/monochrome/apple-icon-57x57.png">
        <link rel="apple-touch-icon" sizes="60x60" href="https://clib.fyers.in/fyers_logos/monochrome/apple-icon-60x60.png">
        <link rel="apple-touch-icon" sizes="72x72" href="https://clib.fyers.in/fyers_logos/monochrome/apple-icon-72x72.png">
        <link rel="apple-touch-icon" sizes="76x76" href="https://clib.fyers.in/fyers_logos/monochrome/apple-icon-76x76.png">
        <link rel="apple-touch-icon" sizes="114x114" href="https://clib.fyers.in/fyers_logos/monochrome/apple-icon-114x114.png">
        <link rel="apple-touch-icon" sizes="120x120" href="https://clib.fyers.in/fyers_logos/monochrome/apple-icon-120x120.png">
        <link rel="apple-touch-icon" sizes="144x144" href="https://clib.fyers.in/fyers_logos/monochrome/apple-icon-144x144.png">
        <link rel="apple-touch-icon" sizes="152x152" href="https://clib.fyers.in/fyers_logos/monochrome/apple-icon-152x152.png">
        <link rel="apple-touch-icon" sizes="180x180" href="https://clib.fyers.in/fyers_logos/monochrome/apple-icon-180x180.png">
        <link rel="icon" type="image/png" sizes="192x192"  href="https://clib.fyers.in/fyers_logos/monochrome/android-icon-192x192.png">
        <link rel="icon" type="image/png" sizes="32x32" href="https://clib.fyers.in/fyers_logos/monochrome/favicon-32x32.png">
        <link rel="icon" type="image/png" sizes="96x96" href="https://clib.fyers.in/fyers_logos/monochrome/favicon-96x96.png">
        <link rel="icon" type="image/png" sizes="16x16" href="https://clib.fyers.in/fyers_logos/monochrome/favicon-16x16.png">
        <link rel="manifest" href="https://clib.fyers.in/fyers_logos/monochrome/manifest.json">
        <meta name="msapplication-TileColor" content="#ffffff">
        <meta name="msapplication-TileImage" content="https://clib.fyers.in/fyers_logos/monochrome/ms-icon-144x144.png">
        <link rel="stylesheet" type="text/css" href="https://clib.fyers.in/lib/bootstrap/3.3.7/bootstrap.min.css">
        <link rel="stylesheet" href="https://clib.fyers.in/lib/animate/3.5.2/animate.min.css">
        <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js"></script>
        <script>
            // Redundancy
           window.jQuery || document.write('<script src="https://clib.fyers.in/lib/jquery/1.12.4/jquery.min.js"><\/script>');
        </script>
        <script type="text/javascript" src="https://clib.fyers.in/lib/bootstrap/3.3.7/bootstrap.min.js"></script> 
        <link href='https://fonts.googleapis.com/css?family=Work+Sans:400,300,700' rel='stylesheet' type='text/css'>
        <script async src="https://www.google-analytics.com/analytics.js"></script>

        <link rel="stylesheet" href="https://clib.fyers.in/styles/fy_login.css">

        %s
    </head>

    <body style="font-family:Calibri;">
        %s
        <div class="container col-md-4 " style="min-width: 300px;">
        <div class="row">
        <div id="newmsg" class="profile profile--open">
        <div class="profile__form" id="changepass">
        <div class="profile__fields">
            <h3>Change Your Password</h3>
            <hr>
            %s

            <form method="POST" action="./change" id="RegisterNewUser" >
                <input type="hidden" id="typeFlag" name="typeFlag" value="5" />
                <input type="hidden" id="fyers_id" name="fyers_id" value="%s" />
                <input type="hidden" id="cb" name="cb" value="%s" />
                <div class="field">
                    <input type="password" class="form-control" name="newChangePwd" placeholder="New Password" id="newChangePwd"   style="height: 40px;" required="required">
                </div>
                <div class="field">
                    <input type="password" class="form-control" name="confirmpwd" placeholder="Confirm New Password" id="confirmpwd"   style="height: 40px;" required="required">
                </div>
                <div class="field">
                    <h4>Password Policy:</h4>
                    <span>&nbsp;1.Password Length:Minimum 6 and Maximum 12</span></br>
                    <span>&nbsp;2.Atleast 1 alphabet and 1 numerical</span><br>
                    <span>&nbsp;3.Atleast 1 of the following special character(! or @ or #)</span>
                </div>
                <button type="submit" name = "submitrp" class="btn" id="submitrp" >submit</button>
            </form>
        </div>
        </div>
        </div>
        </div>
        </div>

        <script type="text/javascript">
            $(document).ready(function() {

              $("#newmsg").addClass("profile--open");
              $("#submitrp").click(function (event) {
                  var password = $("#newChangePwd").val();
                  var confirmPassword = $("#confirmpwd").val();
                  if (password != confirmPassword) {
                    alert("Passwords do not match.");
                    event.preventDefault();
                    return false;
                  }
                  return true;
              });
            });
        </script>
    </body>
</html>
""" % (GOOGLE_ANALYTICS_GLOBAL_SITE_TAG,gaTagHead, gaTagBody, gaScript, errorMessage, fyers_id, callbackUrl)
    return changePasswordHtmlVariable
