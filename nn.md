otp
post https://render-backend-ahh7.onrender.com/auth/send-otp
body  {"mobile_number":"9854254668"}
rsponse {
    "success": true,
    "message": "OTP sent successfully.",
    "mobile_number": "9854254668"
}

====================================

login
post https://render-backend-ahh7.onrender.com/auth/login
body {"mobile_number":"9854254668",
"otp":"897973"}
resposne {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODU0MjU0NjY4IiwiZXhwIjoxNzQ2NTIyODUzfQ.83NuSL_beYQUrmXQkW1fB1oMG7oLm73vunR-DiTmkl8",
    "token_type": "bearer"
}
====================================


get https://render-backend-ahh7.onrender.com/patients/home_user
header beaarer token
boby none
response{
    "patient": {
        "name": "newname",
        "mobile_number": "9854254668",
        "email": "string",
        "address": "string",
        "date_of_birth": "2025-05-04T03:53:35.654000",
        "id": "1TaHTj",
        "created_at": "2025-05-04T04:00:44.215457"
    },
    "appointments": []
}