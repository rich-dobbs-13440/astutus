var astutus = {

    deleteAfterConfirmation: function (prompt, url) {
        if (confirm(prompt)) {
            const xhr = new XMLHttpRequest();
            xhr.onload = () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    if (xhr.status == 202) {
                        redirectURL = xhr.response["redirect_url"]
                        if (redirectURL != undefined) {
                            window.location.replace(redirectURL);
                        }
                    }
                } else {
                    console.log('deleteAfterConfirmation failed.  xhr:', xhr);
                    alert('The method deleteAfterConfirmation failed.  xhr:' + xhr)
                }
            };
            if (url == undefined) {
                xhr.open('DELETE', "");
            } else {
                xhr.open('DELETE', url);
            }
            xhr.responseType = 'json';
            xhr.send();
        }
    }

}

