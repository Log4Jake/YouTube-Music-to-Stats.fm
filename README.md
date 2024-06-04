# YouTube-Music-to-Stats.fm
This is a tool that converts YouTube music streams to the Spotify format that stats.fm uses. I must mention a word of warning. Stats.fm can ban you from their service for using "altered files". Please do not abuse this tool to boost your stats. I made this to fill in some gaps in people's streaming history on stats.fm from when they used YT Music. PLEASE DO NOT ABUSE THIS YOU COULD GET BANNED!

## A word to the Devs
To the great developers at stats.fm, I hope one day you can bring support for YouTube/YouTube Music. When that day comes (if ever) I will be extremely happy. :) Until then here is this simple tool to convert past YouTube streams to the Spotify JSON format.

## Disclaimer for converting multiple users' streams.
Please do not process multiple users at the same time there are still some bugs that need to be worked out. If processing multiple users. After each user delete the `.cache` file and the `upload` and `download` folder before running the script again. Eventually, I will fix this bug.

# How to Use.
First, you must have your file from https://takeout.google.com/
1. Press Deselect All.

![image](https://github.com/Log4Jake/YouTube-Music-to-Stats.fm/assets/62357760/fae95a3b-f80d-4ab2-82d8-48b2c6614649)

2. Scroll to the bottom and select YouTube.

![image](https://github.com/Log4Jake/YouTube-Music-to-Stats.fm/assets/62357760/8017ce4e-5134-482a-b7bb-51008845500e)

3. Select the Multiple Formats Button then scroll to the bottom and change the History option from HTML to JSON.

![image](https://github.com/Log4Jake/YouTube-Music-to-Stats.fm/assets/62357760/48514349-ef06-4fa2-94cd-4027b37d16b8)

4. Click OK then proceed through the next steps on takeout.

5. Once you have received, downloaded, and extracted your takeout you can locate the watch-history.json file in `takeout-datehere\Takeout\YouTube and YouTube Music\history`

6. Download this repo and extract it. Or use `git clone https://github.com/Log4Jake/YouTube-Music-to-Stats.fm.git`

7. Open the folder/directory.

8. Make sure you have python3 or higher. Once Downloaded you can run `pip install -r requirements.txt`

9. Then run `python3 .\generatekey.py` You should get an output like this. Save this key somewhere for later.

![image](https://github.com/Log4Jake/YouTube-Music-to-Stats.fm/assets/62357760/36de82d3-a534-4d4b-b5ce-2fae878de49f)

10. Open the `app.py` file with your code editor or notepad and find these lines.

![image](https://github.com/Log4Jake/YouTube-Music-to-Stats.fm/assets/62357760/2a2d9490-c544-49f1-858d-f61744e8a359)


11. Inside the `''` add your keys from `generatekey.py` and from https://developer.spotify.com/ You will want to create an app with the web API. Add `http://localhost:5000/callback` as the callback URL.

12. Once that is finished run `python3 .\app.py` You should see this.

![image](https://github.com/Log4Jake/YouTube-Music-to-Stats.fm/assets/62357760/99dbffd1-56b5-4762-ba6e-b2dd9456a1b0)


13. Open http://127.0.0.1:5000/ in your browser.

![image](https://github.com/Log4Jake/YouTube-Music-to-Stats.fm/assets/62357760/b569d545-195c-47b4-b6dc-a8f2a8a88976)

14. Then log in with Spotify and authorize your app.

15. You should then redirect to the upload page. Browse and select your `watch-history.json` file. Then select upload and it should process your data. This can take a while. Once it is finished your file will download automatically.

![image](https://github.com/Log4Jake/YouTube-Music-to-Stats.fm/assets/62357760/ca2ce95b-9d1a-4ffd-ab16-286151b666a5)

16. You can then upload this file to stats.fm or any other service you use. Please make sure you are following the Terms of Service.
# Want to support me?
<a href="https://www.buymeacoffee.com/Log4Jake" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
