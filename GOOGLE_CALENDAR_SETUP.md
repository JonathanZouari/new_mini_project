# Google Calendar Setup Guide / מדריך הגדרת Google Calendar

**Languages:** English | עברית

---

## English Instructions

### Overview
This guide will help you set up Google Calendar API integration for the WhatsApp Appointment Scheduler. You'll create a service account and obtain credentials to allow the bot to create calendar events.

---

### Prerequisites
- A Google Account
- Access to [Google Cloud Console](https://console.cloud.google.com)

---

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click on the project dropdown at the top of the page
3. Click **"New Project"**
4. Enter a project name (e.g., "WhatsApp Scheduler")
5. Click **"Create"**
6. Wait for the project to be created (this may take a few seconds)

---

### Step 2: Enable Google Calendar API

1. Make sure your new project is selected in the dropdown
2. Go to **"APIs & Services"** > **"Library"**
3. Search for **"Google Calendar API"**
4. Click on **"Google Calendar API"**
5. Click **"Enable"**
6. Wait for the API to be enabled

---

### Step 3: Create a Service Account

1. Go to **"APIs & Services"** > **"Credentials"**
2. Click **"Create Credentials"** at the top
3. Select **"Service Account"**
4. Fill in the service account details:
   - **Service account name**: `whatsapp-scheduler` (or any name you prefer)
   - **Service account ID**: Will be auto-generated
   - **Description**: "Service account for WhatsApp appointment scheduler"
5. Click **"Create and Continue"**
6. **Grant access** (Optional): Skip this step by clicking **"Continue"**
7. **Grant users access** (Optional): Skip this step by clicking **"Done"**

---

### Step 4: Create Service Account Key

1. On the **"Credentials"** page, find your newly created service account
2. Click on the service account email (e.g., `whatsapp-scheduler@...iam.gserviceaccount.com`)
3. Go to the **"Keys"** tab
4. Click **"Add Key"** > **"Create new key"**
5. Select **"JSON"** as the key type
6. Click **"Create"**
7. A JSON file will be downloaded to your computer (e.g., `whatsapp-scheduler-xxxxx.json`)
8. **Important**: Keep this file secure! It contains sensitive credentials.

---

### Step 5: Set Up Your Project Directory

1. In your project folder, create a `credentials` directory:
   ```bash
   mkdir credentials
   ```

2. Move the downloaded JSON file to the `credentials` folder:
   ```bash
   mv ~/Downloads/whatsapp-scheduler-xxxxx.json ./credentials/google_calendar_credentials.json
   ```

3. Your project structure should look like this:
   ```
   new_mini_project/
   ├── credentials/
   │   └── google_calendar_credentials.json  ← Your credentials file
   ├── crew.py
   ├── app.py
   ├── google_calendar_helper.py
   ├── .env
   └── ...
   ```

---

### Step 6: Configure Environment Variables

1. Create a `.env` file in your project root (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and update the Google Calendar settings:
   ```env
   # Google Calendar API
   GOOGLE_CALENDAR_CREDENTIALS_PATH=./credentials/google_calendar_credentials.json
   GOOGLE_CALENDAR_ID=primary
   ```

   **Notes:**
   - `GOOGLE_CALENDAR_CREDENTIALS_PATH`: Path to your JSON credentials file
   - `GOOGLE_CALENDAR_ID`: Use `primary` for the service account's default calendar, or specify a calendar ID

---

### Step 7: Share Calendar with Service Account

**Important:** The service account needs access to your calendar!

1. Open the JSON credentials file and find the `client_email` field:
   ```json
   {
     "client_email": "whatsapp-scheduler@your-project.iam.gserviceaccount.com",
     ...
   }
   ```

2. Copy the email address (e.g., `whatsapp-scheduler@your-project.iam.gserviceaccount.com`)

3. Go to [Google Calendar](https://calendar.google.com)

4. On the left sidebar, find **"My calendars"**

5. Hover over the calendar you want to use and click the three dots **⋮**

6. Click **"Settings and sharing"**

7. Scroll down to **"Share with specific people"**

8. Click **"Add people"**

9. Paste the service account email address

10. Set permission to **"Make changes to events"**

11. Click **"Send"**

---

### Step 8: (Optional) Use a Specific Calendar

If you want to use a specific calendar instead of the primary one:

1. In Google Calendar settings, find **"Integrate calendar"**
2. Copy the **"Calendar ID"** (looks like: `abc123@group.calendar.google.com`)
3. Update your `.env` file:
   ```env
   GOOGLE_CALENDAR_ID=abc123@group.calendar.google.com
   ```

---

### Step 9: Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

This will install:
- `google-auth`
- `google-auth-oauthlib`
- `google-auth-httplib2`
- `google-api-python-client`

---

### Step 10: Test the Integration

Run the test script to verify everything is working:

```bash
python google_calendar_helper.py
```

You should see:
```
✅ Google Calendar service initialized successfully
📅 Using calendar: primary
📅 Creating test event...
✅ Appointment scheduled successfully!
```

Check your Google Calendar to see if the test event was created!

---

### Troubleshooting

**Error: "Credentials file not found"**
- Check that the path in `.env` is correct
- Verify the JSON file exists in the `credentials` folder

**Error: "Access denied" or "403 Forbidden"**
- Make sure you shared the calendar with the service account email
- Check that the service account has "Make changes to events" permission

**Error: "Calendar not found"**
- Verify the `GOOGLE_CALENDAR_ID` in `.env`
- Use `primary` for the default calendar

**Events not appearing in calendar**
- Check that you're looking at the correct calendar
- Verify the service account email has access
- Check the date/time of the event

---

### Security Best Practices

1. **Never commit credentials to Git**:
   ```bash
   # Add to .gitignore
   credentials/
   .env
   ```

2. **Restrict service account permissions**: Only grant access to the specific calendar needed

3. **Rotate credentials regularly**: Delete old keys and create new ones periodically

4. **Keep credentials secure**: Store the JSON file in a secure location with restricted access

---

---

## הוראות בעברית

### סקירה כללית
מדריך זה יעזור לך להגדיר אינטגרציה עם Google Calendar API עבור מתזמן הפגישות בוואטסאפ. תיצור חשבון שירות (Service Account) ותקבל אישורים שיאפשרו לבוט ליצור אירועים ביומן.

---

### דרישות מוקדמות
- חשבון Google
- גישה ל-[Google Cloud Console](https://console.cloud.google.com)

---

### שלב 1: יצירת פרויקט ב-Google Cloud

1. היכנס ל-[Google Cloud Console](https://console.cloud.google.com)
2. לחץ על תפריט הפרויקטים בחלק העליון של הדף
3. לחץ על **"New Project"** (פרויקט חדש)
4. הזן שם לפרויקט (לדוגמה: "WhatsApp Scheduler")
5. לחץ על **"Create"** (צור)
6. המתן ליצירת הפרויקט (עשוי לקחת כמה שניות)

---

### שלב 2: הפעלת Google Calendar API

1. ודא שהפרויקט החדש שלך נבחר בתפריט הנפתח
2. עבור ל-**"APIs & Services"** > **"Library"**
3. חפש **"Google Calendar API"**
4. לחץ על **"Google Calendar API"**
5. לחץ על **"Enable"** (הפעל)
6. המתן להפעלת ה-API

---

### שלב 3: יצירת Service Account

1. עבור ל-**"APIs & Services"** > **"Credentials"** (אישורים)
2. לחץ על **"Create Credentials"** בחלק העליון
3. בחר **"Service Account"** (חשבון שירות)
4. מלא את פרטי חשבון השירות:
   - **Service account name**: `whatsapp-scheduler` (או כל שם אחר)
   - **Service account ID**: יווצר אוטומטית
   - **Description**: "Service account for WhatsApp appointment scheduler"
5. לחץ על **"Create and Continue"**
6. **Grant access** (אופציונלי): דלג על שלב זה בלחיצה על **"Continue"**
7. **Grant users access** (אופציונלי): דלג על שלב זה בלחיצה על **"Done"**

---

### שלב 4: יצירת מפתח ל-Service Account

1. בדף **"Credentials"**, מצא את חשבון השירות שיצרת
2. לחץ על כתובת המייל של חשבון השירות (לדוגמה: `whatsapp-scheduler@...iam.gserviceaccount.com`)
3. עבור לטאב **"Keys"** (מפתחות)
4. לחץ על **"Add Key"** > **"Create new key"**
5. בחר **"JSON"** כסוג המפתח
6. לחץ על **"Create"**
7. קובץ JSON יורד למחשב שלך (לדוגמה: `whatsapp-scheduler-xxxxx.json`)
8. **חשוב**: שמור על הקובץ במקום מאובטח! הוא מכיל אישורים רגישים.

---

### שלב 5: הגדרת תיקיית הפרויקט

1. בתיקיית הפרויקט שלך, צור תיקיית `credentials`:
   ```bash
   mkdir credentials
   ```

2. העבר את קובץ ה-JSON שהורד לתיקיית `credentials`:
   ```bash
   mv ~/Downloads/whatsapp-scheduler-xxxxx.json ./credentials/google_calendar_credentials.json
   ```

3. מבנה הפרויקט שלך צריך להיראות כך:
   ```
   new_mini_project/
   ├── credentials/
   │   └── google_calendar_credentials.json  ← קובץ האישורים שלך
   ├── crew.py
   ├── app.py
   ├── google_calendar_helper.py
   ├── .env
   └── ...
   ```

---

### שלב 6: הגדרת משתני סביבה

1. צור קובץ `.env` בשורש הפרויקט (העתק מ-`.env.example`):
   ```bash
   cp .env.example .env
   ```

2. ערוך את קובץ `.env` ועדכן את הגדרות Google Calendar:
   ```env
   # Google Calendar API
   GOOGLE_CALENDAR_CREDENTIALS_PATH=./credentials/google_calendar_credentials.json
   GOOGLE_CALENDAR_ID=primary
   ```

   **הערות:**
   - `GOOGLE_CALENDAR_CREDENTIALS_PATH`: נתיב לקובץ אישורי ה-JSON
   - `GOOGLE_CALENDAR_ID`: השתמש ב-`primary` עבור היומן ברירת המחדל, או ציין מזהה יומן ספציפי

---

### שלב 7: שיתוף היומן עם ה-Service Account

**חשוב:** חשבון השירות צריך גישה ליומן שלך!

1. פתח את קובץ אישורי ה-JSON ומצא את שדה `client_email`:
   ```json
   {
     "client_email": "whatsapp-scheduler@your-project.iam.gserviceaccount.com",
     ...
   }
   ```

2. העתק את כתובת המייל (לדוגמה: `whatsapp-scheduler@your-project.iam.gserviceaccount.com`)

3. עבור ל-[Google Calendar](https://calendar.google.com)

4. בסרגל הצד השמאלי, מצא את **"היומנים שלי"** ("My calendars")

5. הצב את העכבר מעל היומן שברצונך להשתמש בו ולחץ על שלוש הנקודות **⋮**

6. לחץ על **"הגדרות ושיתוף"** ("Settings and sharing")

7. גלול למטה ל-**"שיתוף עם אנשים ספציפיים"** ("Share with specific people")

8. לחץ על **"הוספת אנשים"** ("Add people")

9. הדבק את כתובת המייל של חשבון השירות

10. הגדר הרשאה ל-**"ביצוע שינויים באירועים"** ("Make changes to events")

11. לחץ על **"שלח"** ("Send")

---

### שלב 8: (אופציונלי) שימוש ביומן ספציפי

אם ברצונך להשתמש ביומן ספציפי במקום היומן הראשי:

1. בהגדרות Google Calendar, מצא את **"שילוב יומן"** ("Integrate calendar")
2. העתק את **"מזהה יומן"** ("Calendar ID") - נראה כך: `abc123@group.calendar.google.com`
3. עדכן את קובץ `.env`:
   ```env
   GOOGLE_CALENDAR_ID=abc123@group.calendar.google.com
   ```

---

### שלב 9: התקנת תלויות

התקן את חבילות Python הנדרשות:

```bash
pip install -r requirements.txt
```

זה יתקין:
- `google-auth`
- `google-auth-oauthlib`
- `google-auth-httplib2`
- `google-api-python-client`

---

### שלב 10: בדיקת האינטגרציה

הפעל את סקריפט הבדיקה כדי לוודא שהכל עובד:

```bash
python google_calendar_helper.py
```

אמור להופיע:
```
✅ Google Calendar service initialized successfully
📅 Using calendar: primary
📅 Creating test event...
✅ Appointment scheduled successfully!
```

בדוק ב-Google Calendar שלך אם אירוע הבדיקה נוצר!

---

### פתרון בעיות

**שגיאה: "Credentials file not found"**
- וודא שהנתיב ב-`.env` נכון
- אמת שקובץ ה-JSON קיים בתיקיית `credentials`

**שגיאה: "Access denied" או "403 Forbidden"**
- ודא ששיתפת את היומן עם כתובת המייל של חשבון השירות
- בדוק שלחשבון השירות יש הרשאה "ביצוע שינויים באירועים"

**שגיאה: "Calendar not found"**
- אמת את `GOOGLE_CALENDAR_ID` ב-`.env`
- השתמש ב-`primary` עבור היומן ברירת המחדל

**אירועים לא מופיעים ביומן**
- ודא שאתה מסתכל על היומן הנכון
- אמת שלכתובת המייל של חשבון השירות יש גישה
- בדוק את התאריך/שעה של האירוע

---

### שיטות אבטחה מומלצות

1. **לעולם אל תעלה אישורים ל-Git**:
   ```bash
   # הוסף ל-.gitignore
   credentials/
   .env
   ```

2. **הגבל הרשאות חשבון שירות**: הענק גישה רק ליומן הספציפי הנדרש

3. **החלף אישורים באופן קבוע**: מחק מפתחות ישנים וצור חדשים מעת לעת

4. **שמור על אישורים מאובטחים**: אחסן את קובץ ה-JSON במיקום מאובטח עם גישה מוגבלת

---

## Quick Reference / התייחסות מהירה

### Files Needed / קבצים נדרשים
- ✅ `credentials/google_calendar_credentials.json` - Service account key
- ✅ `.env` - Environment variables with Google Calendar settings

### Environment Variables / משתני סביבה
```env
GOOGLE_CALENDAR_CREDENTIALS_PATH=./credentials/google_calendar_credentials.json
GOOGLE_CALENDAR_ID=primary
```

### Required Packages / חבילות נדרשות
```
google-auth==2.35.0
google-auth-oauthlib==1.2.1
google-auth-httplib2==0.2.0
google-api-python-client==2.149.0
```

### Test Command / פקודת בדיקה
```bash
python google_calendar_helper.py
```

---

## Support / תמיכה

If you encounter any issues, check:
- The credentials file path is correct
- The calendar is shared with the service account email
- All dependencies are installed
- The service account has the correct permissions

אם אתה נתקל בבעיות, בדוק:
- שנתיב קובץ האישורים נכון
- שהיומן משותף עם כתובת המייל של חשבון השירות
- שכל התלויות מותקנות
- שלחשבון השירות יש את ההרשאות הנכונות
