# CursItSchool

💰 Expense Tracker (Python + Tkinter + SQLite)

A desktop application for tracking personal and family expenses, built with Python using Tkinter for the interface and SQLite for persistent data storage.

---------

🧩 Main Features

-User Authentication-
Register and Login with email and password
Password reset with temporary password
Admin account and admin dashboard for managing all users

-Expense Management (CRUD)-
Add, edit, delete, and view expenses
Each expense includes amount, category, date, and description
Category dropdown list
Date picker (calendar selection)

-Filters and Sorting-
Filter by category
Filter by date range (From / To)
Sort by date, amount, or category
Choose ascending or descending order

-Budget Tracking-
Set payday (1–31) and recurring monthly budget
Automatic calculation of remaining amount in the current salary cycle
Live update of "Remaining amount" after each expense
Chart: Remaining amount vs. Days left

-Reports-
Export expenses to .csv and summary to .txt
Choose custom location for saving via file dialog
Automatically open exported files

-Charts and Analytics-
Expense distribution by category and by date
Remaining amount vs. days left (Matplotlib)

-Admin Dashboard-
View all registered users
Promote regular users to admin

-----------

⚙️ Technologies Used

Python 3.10+
Tkinter – GUI framework
SQLite3 – database
Matplotlib – data visualization
tkcalendar – date picker widgets

-----------

🗂️ Project Structure

expense_tracker/
│
├── app.py               # Main application (UI + business logic)
├── database.py          # Database initialization and connection
├── models.py            # Database models and query logic
├── utils.py             # Charts, exports, calculations, helpers
├── requirements.txt     # Dependencies
└── README.md            # Project documentation

------------
🧱 Database Structure

Tables:
users → stores user info (email, hashed password, admin flag)
expenses → stores expenses linked to each user
user_settings → stores payday and monthly budget for each user

------------

📊 Screens

Login & Register
Expense Dashboard
Budget & Remaining Panel
Remaining vs Days chart
Admin User Management

------------

🧠 Future Improvements

Custom categories
Multi-currency support
Monthly analytics summary
Sharing one dashboard between 2 or more users 
