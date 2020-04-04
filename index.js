(function(){
    console.log('checkSystemRequirements');
    console.log(JSON.stringify(ZoomMtg.checkSystemRequirements()));
    ZoomMtg.preLoadWasm();
    ZoomMtg.prepareJssdk();
    ZoomMtg.setZoomJSLib('https://dmogdx0jrul3u.cloudfront.net/1.7.2/lib', '/av')
    // ZoomMtg.setZoomJSLib('https://source.zoom.us/1.7.2/lib', '/av')
    console.log('What now....')
    document.addEventListener('DOMContentLoaded', () => {
      console.log('OOOO')
    document.getElementById('zmmtg-root').addEventListener('click', () => {
console.log('Clicked')
  var meetConfig = {
          apiKey: "Vll7I_NaS6KORk06NjJ8qw",
          apiSecret: "DOMoWSVWYKC7OACsfmbHpi1DDio4owIKqKVm",
          meetingNumber: 4805022087,
          userName: 'Mathieu',
          password: "668116dsdass",
          leaveUrl: window.location.toString(),
          role: 1
      };
      console.log(meetConfig)
      var signature = ZoomMtg.generateSignature({
        meetingNumber: meetConfig.meetingNumber,
        apiKey: meetConfig.apiKey,
        apiSecret: meetConfig.apiSecret,
        role: meetConfig.role
      });
      ZoomMtg.init({
        leaveUrl: 'http://www.zoom.us',
        isSupportAV: true,
        success: function () {
          console.log('Initialize success')
            ZoomMtg.join(
                {
                    meetingNumber: meetConfig.meetingNumber,
                    userName: meetConfig.userName,
                    signature: signature,
                    apiKey: meetConfig.apiKey,
                    userEmail: 'mathieu.chauvinc@omesti.com',
                    passWord: meetConfig.password,
                    success: function(res){
                      console.log('join meeting success');
                        $('#nav-tool').hide();
                    },
                    error: function(res) {
                        console.log(res);
                    }
                }
            );
        },
        error: function(res) {
            console.log(res);
        }
    });
  })
    })
  })()