# hammer.thm
Resources I used to solve the THM Hammer room


## Add target to etc/hosts
```
echo target hammer.thm >> etc/hosts
```

## Scan open ports
`nmap -p- hammer.thm`

Open browser and navigate to hammer.thm:1337

## Gobuster directory bruteforcing
```
gobuster -u http://hammer.thm:1337 -w Tools/wordlists/dirbuster/directory-list-1.0.txt dir
```
![](Assets/gobuster.PNG)
## Sed to substitute hmr_ at the beginning of each directory in the list
```
cp Tools/wordlists/dirbuster/directory-list-1.0.txt list.txt
```
Now to format the entries:
```
sed -i 's/^/hmr_/' list.txt
```
Then use gobuster again with the updated directories list:
```
gobuster -u http://hammer.thm:1337 -w list.txt dir
```
Which gives us the following result:
![](Assets/hmr_gobuster.PNG)
In hmr_logs there is a reference to the user tester@hammer.thm. Great! Let's use that in our reset_password feature.
## Crunch to create OTP list for bruteforcing
From the reset_password.php page, we know it's expecting a 4 digit OTP code
```
crunch 4 4 -o otp.txt -t %%%% -s 0000 -e 9999
```
Note: In hindsight I could have made the range 1000 to 9999 instead, since there were no valid codes from 0000 to 1000

## Use script.py to enumerate 
Challenges: The session ID has a timeout of 5 requests, so I had to keep regenerating session IDs with a POST request to index.php every 5 requests
```
python3 script.py 
```
There will be multiple VALID codes, just keep an eye on the terminal until one pops up and use it

## Change Cookies
Set 'persistentSession: yes' in since there is some logic in the backend that checks for this value to be true to keep it from issuing a logout.

## Enter commands
We find that only ls is valid, and we get the following result from that:
![](Assets/dashboard_ls.PNG)

Download the key by navigating to /188ade1.key.
In cmd line, view contents of this file by typing cat 188ade1.key
![](Assets/188ade1key.PNG)

## JWT
Looking at the dashboard.php source code, we notice that a JWT token accompanies the POST request to /execute_command.php. Analyze this in [jwt.io](https://jwt.io) to find the result:

---

The following code is in /dashboard.php
```
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard</title>
    <link href="/hmr_css/bootstrap.min.css" rel="stylesheet">
    <script src="/hmr_js/jquery-3.6.0.min.js"></script>
    <style>
        body {
            background: url('/hmr_images/hammer.webp') no-repeat center center fixed;
            background-size: cover;
        }
        .container {
            position: relative;
            z-index: 10; /* Make sure the content is above the background */
            background-color: rgba(255, 255, 255, 0.8); /* Slight white background for readability */
            padding: 20px;
            border-radius: 10px;
        }
    </style>
	
	    <script>
       
        function getCookie(name) {
            const value = `; ${document.cookie}`;
            const parts = value.split(`; ${name}=`);
            if (parts.length === 2) return parts.pop().split(';').shift();
        }

      
        function checkTrailUserCookie() {
            const trailUser = getCookie('persistentSession');
            if (!trailUser) {
          
                window.location.href = 'logout.php';
            }
        }

       
        setInterval(checkTrailUserCookie, 1000); 
    </script>

</head>
<body>
<div class="container mt-5">
    <div class="row justify-content-center">
        <div class="col-md-6">
            <h3>Welcome, Thor! - Flag: THM{AuthBypass3D}</h3>
            <p>Your role: user</p>
            
            <div>
                <input type="text" id="command" class="form-control" placeholder="Enter command">
                <button id="submitCommand" class="btn btn-primary mt-3">Submit</button>
                <pre id="commandOutput" class="mt-3"></pre>
            </div>
            
            <a href="logout.php" class="btn btn-danger mt-3">Logout</a>
        </div>
    </div>
</div>

<script>
$(document).ready(function() {
    $('#submitCommand').click(function() {
        var command = $('#command').val();
        var jwtToken = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsImtpZCI6Ii92YXIvd3d3L215a2V5LmtleSJ9.eyJpc3MiOiJodHRwOi8vaGFtbWVyLnRobSIsImF1ZCI6Imh0dHA6Ly9oYW1tZXIudGhtIiwiaWF0IjoxNzM5NDgxNTEzLCJleHAiOjE3Mzk0ODUxMTMsImRhdGEiOnsidXNlcl9pZCI6MSwiZW1haWwiOiJ0ZXN0ZXJAaGFtbWVyLnRobSIsInJvbGUiOiJ1c2VyIn19.tR8jR6pKAO6m677TejA1mHH2vQ_keHgZxU3GReFq8N0';

        // Make an AJAX call to the server to execute the command
        $.ajax({
            url: 'execute_command.php',
            method: 'POST',
            data: JSON.stringify({ command: command }),
            contentType: 'application/json',
            headers: {
                'Authorization': 'Bearer ' + jwtToken
            },
            success: function(response) {
                $('#commandOutput').text(response.output || response.error);
            },
            error: function() {
                $('#commandOutput').text('Error executing command.');
            }
        });
    });
});
</script>
</body>
</html>
```

---

Notice a JWT reference to  eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsImtpZCI6Ii92YXIvd3d3L215a2V5LmtleSJ9.eyJpc3MiOiJodHRwOi8vaGFtbWVyLnRobSIsImF1ZCI6Imh0dHA6Ly9oYW1tZXIudGhtIiwiaWF0IjoxNzM5NDgxNTEzLCJleHAiOjE3Mzk0ODUxMTMsImRhdGEiOnsidXNlcl9pZCI6MSwiZW1haWwiOiJ0ZXN0ZXJAaGFtbWVyLnRobSIsInJvbGUiOiJ1c2VyIn19.tR8jR6pKAO6m677TejA1mHH2vQ_keHgZxU3GReFq8N0

Decoding this gives
[this result](https://jwt.io/#debugger-io?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsImtpZCI6Ii92YXIvd3d3L215a2V5LmtleSJ9.eyJpc3MiOiJodHRwOi8vaGFtbWVyLnRobSIsImF1ZCI6Imh0dHA6Ly9oYW1tZXIudGhtIiwiaWF0IjoxNzM5NDgxNTEzLCJleHAiOjE3Mzk0ODUxMTMsImRhdGEiOnsidXNlcl9pZCI6MSwiZW1haWwiOiJ0ZXN0ZXJAaGFtbWVyLnRobSIsInJvbGUiOiJ1c2VyIn19.tR8jR6pKAO6m677TejA1mHH2vQ_keHgZxU3GReFq8N0)

Change the role to admin - 401 Unauthorized

Change the key to /var/www/html/188ade1.key - 401 Unauthorized

Change the secret key to the value of 188ade1.key - 200

The final JWT token is [this](https://jwt.io/#debugger-io?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsImtpZCI6Ii92YXIvd3d3L2h0bWwvMTg4YWRlMS5rZXkifQ.eyJpc3MiOiJodHRwOi8vaGFtbWVyLnRobSIsImF1ZCI6Imh0dHA6Ly9oYW1tZXIudGhtIiwiaWF0IjoxNzM5NDgwMjE5LCJleHAiOjE3Mzk0ODM4MTksImRhdGEiOnsidXNlcl9pZCI6MSwiZW1haWwiOiJ0ZXN0ZXJAaGFtbWVyLnRobSIsInJvbGUiOiJhZG1pbiJ9fQ.9sNBOr1gkBgs3_hetViDicpXzRQll6jMJ47RiNIPsKI)

Change the body of the request to obtain the flag in the directory /home/ubuntu/flag.txt.
![](Assets/POSTrequest.PNG)

Under the Response tab, the following JSON is observed:
`output	"THM{RUNANYCOMMAND1337}\n"`
