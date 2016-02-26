<!DOCTYPE html>
<html lang="en">
<head>

    <title>LearningRegistry :: OAuth Management</title>

    <link rel="stylesheet" type="text/css" href="css/style.css">
<!-- We use client cookies to save the user credentials -->
<script src="angular/angular.min.js"></script>
<script src="angular/angular-animate.min.js"></script>
<script src="angular/angular-route.min.js"></script>
<script src="angular/angular-sanitize.min.js"></script>
<script src="controllers/project.js"></script>


<script src="//cdn.jsdelivr.net/satellizer/0.13.4/satellizer.min.js"></script>
<!-- Setting the right viewport -->
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
</head>
<body ng-app="main" ng-controller="LoginCtrl">

<!-- login.tpl.html -->
<!-- ... -->
<button ng-click="authenticate('google')">Sign in with Google</button><br>
<button ng-click="authenticate('facebook')">Sign in with facebook</button><br>
<!-- ... -->

<p ng-repeat="(key, value) in results.oauth.consumer_keys">{{key}}{{value}}</p>
    <div class="msg"></div>
    <div ng-show="showdetails">
    <div class="oauth">
      <fieldset>
        <legend>Publish Password</legend>
        <p>Using your email address as username and this password, you may publish to the Basic Publish or SWORD interfaces your own digitally signed resource data envelopes.</p>
        <div class="form-group">
        <label for="password_set">Is Password Set?</label>
        <input type="checkbox" id="password_set" disabled="disabled">
        </div>
        <label for="password">Password</label>
        <input type="password" id="password">

        <label for="verify_password">Verify Password</label>
        <input type="password" id="verify_password">
        <button id="save_password">Save</button>
      </fieldset>
      <fieldset>
        <legend>Signing Information</legend>
        <p>The following will be appended to the resource data document's identity signer field along with your email address so that your submissions may be identified.</p>
        <label for="full_name">Full Name</label>
        <input type="text" id="full_name">

        <button id="info_update">Save</button>
      </fieldset>
      <fieldset>
        <legend>2-Legged OAuth Config</legend>
        <p>Use the following when connecting your application to LR to sign on your behalf.  If the OAuth signature is present when you publish, the documents you publish will be signed by the node.</p>
        <div ng-repeat="(key, value) in results.oauth.consumer_keys">
        <label for="consumer_key">oauth_consumer_key</label>
        <input type="text" disabled="disabled" id="consumer_key" value="{{key}}">

        <label for="consumer_secret">oauth_consumer_secret</label>
        <input type="text" disabled="disabled" id="consumer_secret" value="{{value}}">

        </div>
        <div ng-repeat="(key, value) in results.oauth.tokens">
        <label for="token">oauth_token</label>
        <input type="text" disabled="disabled" id="token" value="{{key}}">

        <label for="token_secret">oauth_token_secret</label>
        <input type="text" disabled="disabled" id="token_secret" value="{{value}}">
        </div>
        <button id="regenerate">Revoke and Regenerate</button>
      </fieldset>

    </div>
    </div>
</body>
</html>