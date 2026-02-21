<%@ Page Language="C#" AutoEventWireup="true" %>

<!DOCTYPE html>
<html lang="en">
<head runat="server">
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>🎂 Happy Birthday! 🎉</title>
    <style>
        body {
            margin: 0;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background: linear-gradient(135deg, #ff9a9e, #fad0c4, #ffd1ff);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #fff;
            overflow: hidden;
        }

        .container {
            text-align: center;
            padding: 40px;
            background: rgba(255, 255, 255, 0.18);
            border-radius: 24px;
            backdrop-filter: blur(12px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
            max-width: 90%;
            animation: float 7s ease-in-out infinite;
        }

        h1 {
            font-size: 5.5rem;
            margin: 0 0 20px;
            text-shadow: 0 0 30px rgba(255,255,255,0.9);
        }

        .name {
            font-size: 3.8rem;
            margin: 15px 0 35px;
            color: #fffacd;
            text-shadow: 0 0 20px #ffd700;
        }

        .cake {
            font-size: 9rem;
            margin: 20px 0 30px;
            animation: bounce 2.2s infinite;
        }

        p {
            font-size: 1.6rem;
            line-height: 1.7;
            margin: 15px 0;
        }

        .balloons {
            position: absolute;
            inset: 0;
            pointer-events: none;
        }

        .balloon {
            position: absolute;
            bottom: -180px;
            width: 70px;
            height: 90px;
            border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%;
            animation: rise 14s linear infinite;
        }

        .balloon:nth-child(1) { left: 8%;  background: #ff4757; animation-duration: 16s; }
        .balloon:nth-child(2) { left: 22%; background: #1e90ff; animation-duration: 18s; animation-delay: 2s; }
        .balloon:nth-child(3) { left: 38%; background: #ffeb3b; animation-duration: 15s; animation-delay: 4s; }
        .balloon:nth-child(4) { left: 55%; background: #7fffd4; animation-duration: 17s; animation-delay: 1s; }
        .balloon:nth-child(5) { left: 72%; background: #ff9ff3; animation-duration: 13s; animation-delay: 5s; }
        .balloon:nth-child(6) { left: 88%; background: #ffa502; animation-duration: 19s; animation-delay: 3s; }

        @keyframes rise {
            0%   { transform: translateY(0) rotate(0deg); }
            100% { transform: translateY(-130vh) rotate(720deg); }
        }

        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50%      { transform: translateY(-25px); }
        }

        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50%      { transform: translateY(-25px); }
        }
    </style>
</head>
<body>

    <div class="balloons">
        <div class="balloon"></div>
        <div class="balloon"></div>
        <div class="balloon"></div>
        <div class="balloon"></div>
        <div class="balloon"></div>
        <div class="balloon"></div>
    </div>

    <div class="container">
        <div class="cake">🎂</div>
        <h1>Happy Birthday!</h1>
        <div class="name">Dear Friend 🎈</div>

        <p>May your day be filled with joy, laughter,<br>
           sweet surprises, and all the love you deserve 💖</p>

        <p>Wishing you a fantastic year ahead full of<br>
           health, success, happiness and beautiful moments ✨</p>

        <p>Have the most wonderful birthday ever! 🥳🎉</p>
    </div>

</body>
</html>