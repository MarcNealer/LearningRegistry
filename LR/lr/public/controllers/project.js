/**
 * Created by marc on 20/02/16.
 */
// LoginCtrl.js
var main = angular.module('main',['satellizer'])
  .config(function($authProvider) {
    $authProvider.facebook({
      clientId: '573549156130752',
      responseType: 'token'
    });

    $authProvider.google({
      url: 'auth',
      clientId: '736057767942-dcoohifkad202c7hsm74jhm2ctjrqrlr.apps.googleusercontent.com',
      responseType: 'token',
      redirectUri: window.location.origin + '/auth/',
    });

    $authProvider.github({
      url: 'test',
      clientId: 'a7a036b4bd9702ffa615',
      redirectUri: 'http://localhost:8000/test',
      responseType: 'token'
    });

    $authProvider.linkedin({
      clientId: 'LinkedIn Client ID'
    });

    $authProvider.instagram({
      clientId: 'Instagram Client ID'
    });

    $authProvider.yahoo({
      authorizationEndpoint: 'https://www.amazon.com/ap/oa/',
      clientId: 'amzn1.application-oa2-client.6b06bff7297c4cb5bb5c021cf1e8b2c0',
      scope: ['profile','profile:user_id','postal_code'],
      responseType: 'token',
      redirectUri: 'http://localhost:8000/test',
      state: "STATE"
    });

    $authProvider.live({
      url: 'test',
      clientId: '000000004C181391',
      redirectUri: 'http://localhost:8000/test',
      responseType: 'token'
    });

    $authProvider.twitch({
      clientId: 'Twitch Client ID'
    });

    $authProvider.bitbucket({
      clientId: 'Bitbucket Client ID'
    });

    // No additional setup required for Twitter

    $authProvider.oauth2({
      name: 'foursquare',
      url: '/auth/foursquare',
      clientId: 'Foursquare Client ID',
      redirectUri: window.location.origin,
      authorizationEndpoint: 'https://foursquare.com/oauth2/authenticate',
    });

  });

main.controller('LoginCtrl', function($scope, $auth,$http) {
    $scope.showdetails = false;

    $scope.authenticate = function(provider) {
      $auth.authenticate(provider)
          .then(function(response) {
              $scope.auth_response = response;
              $scope.token = $auth.getToken();
              if (provider =='google') {
                  $http.get('https://www.googleapis.com/plus/v1/people/me?access_token=' + $scope.token)
                      .success(function (data) {
                          $scope.useremail = data.emails[0].value;
                          $scope.sendToServer($scope.useremail);
                      })
              };
              if (provider =='facebook') {
                  $http.get('https://graph.facebook.com/me/?access_token='+ $scope.token + '&&fields=email')
                      .success(function (data) {
                          $scope.useremail=data.email;
                          $scope.sendToServer($scope.useremail);
                      });
              }


          })
          .catch( function(response) {
              $scope.auth_response = response;

          });
    };

    $scope.sendToServer = function(useremail) {
        payload = "name=" + encodeURIComponent($scope.useremail) + "&node_sign_token="+encodeURIComponent($scope.generateSecret(32))+ "&consumer_key=" + encodeURIComponent($scope.generateSecret(32));
        $scope.payload = payload;
        $http.post('/newauth/', $scope.payload,{})
            .success(function(data) {
                $scope.results=data;
                $scope.showdetails=true;
            });

    };
    $scope.generateSecret = function(length) {
        var tab = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
        var secret = '';
        for (var i = 0; i < length; i++) {
            secret += tab.charAt(Math.floor(Math.random() * 64));
        }
        return secret;
    };

  });