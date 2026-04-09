# Productivity Tracker

A comprehensive full-stack web application built with Django for managing tasks, journal entries, and habits with analytics and productivity insights.

##  Features

###  Task Management
- Create, edit, delete, and complete tasks
- Categorize tasks (Work, Study, Personal, Health, Finance, Other)
- Set priorities (Low, Medium, High, Urgent)
- Due date tracking with overdue notifications
- Tag system for better organization
- Task filtering and search

###  Journal Module
- Daily journal entries with mood tracking
- Weather and productivity metrics
- Tag system with hashtags
- Calendar view for entries
- Export functionality
- Journal templates and prompts

###  Habit Tracker
- Create and manage daily/weekly habits
- Track completion streaks
- Visual progress indicators
- Habit categories and customization
- Calendar integration

###  Dashboard & Analytics
- Real-time productivity overview
- Interactive charts with Chart.js
- Task completion trends
- Mood tracking analytics
- Habit completion statistics
- Motivational quotes

###  User Management
- User registration and authentication
- Profile management with preferences
- Dark/Light theme toggle
- Settings and customization

##  Tech Stack

- **Backend:** Django (Python)
- **Frontend:** HTML, CSS, JavaScript, Bootstrap 5
- **Database:** SQLite (development)
- **Charts:** Chart.js
- **Calendar:** FullCalendar.js
- **Icons:** Bootstrap Icons

##  Project Structure

```
productivity_tracker/
├── manage.py
├── productivity_tracker/          # Main Django project
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── users/                         # Authentication & profiles
├── tasks/                         # Task management
├── journal/                       # Journal entries
├── habits/                        # Habit tracking
├── dashboard/                     # Dashboard & analytics
├── templates/                     # HTML templates
├── static/                        # CSS, JS, images
├── media/                         # User uploads
└── db.sqlite3                     # Database
```

##  Getting Started

### Prerequisites
- Python 3.8+
- Django 5.2+
- Pillow (for image handling)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd productivity_tracker
   ```

2. **Install dependencies**
   ```bash
   pip install django pillow
   ```

3. **Run migrations**
   ```bash
   python manage.py migrate
   ```

4. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

5. **Populate sample data (optional)**
   ```bash
   python manage.py populate_sample_data
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Open http://127.0.0.1:8000 in your browser
   - Login with admin/admin123 (demo account)

##  Usage

### Dashboard
- View today's tasks, habits, and journal entries
- Quick stats and productivity overview
- Motivational quotes
- Quick action buttons

### Tasks
- Create tasks with categories, priorities, and due dates
- Mark tasks as complete/incomplete
- Filter tasks by status, category, or priority
- View task details and history

### Journal
- Write daily journal entries
- Track mood and productivity metrics
- Use templates and prompts for inspiration
- View entries in calendar format

### Habits
- Create daily or weekly habits
- Track completion streaks
- Monitor progress over time
- Set reminders and goals

### Analytics
- View productivity trends
- Analyze task completion patterns
- Track mood changes over time
- Monitor habit consistency

##  Customization

### Themes
- Light/Dark mode toggle
- Customizable color schemes
- Responsive design for all devices

### Settings
- Email notification preferences
- Theme selection
- Privacy settings
- Language preferences

##  Development

### Adding New Features
1. Create new Django app: `python manage.py startapp app_name`
2. Add models in `models.py`
3. Create views in `views.py`
4. Add URL patterns in `urls.py`
5. Create templates in `templates/app_name/`
6. Run migrations: `python manage.py makemigrations && python manage.py migrate`

### Database Management
- **Reset database:** Delete `db.sqlite3` and run migrations
- **Backup data:** Copy `db.sqlite3` file
- **Sample data:** Run `python manage.py populate_sample_data`

##  API Endpoints

- `/api/task-stats/` - Task completion statistics
- `/api/habit-stats/` - Habit completion data
- `/api/mood-stats/` - Mood tracking analytics

##  Deployment

### Production Setup
1. Set `DEBUG = False` in settings.py
2. Configure production database (PostgreSQL recommended)
3. Set up static file serving
4. Configure email backend for notifications
5. Set up web server (Nginx + Gunicorn)

### Environment Variables
```bash
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=postgresql://user:password@localhost/dbname
```

### Render/Railway Quick Deploy
1. Add environment variables from `.env.example`.
2. Set `DEBUG=False`.
3. Set `DATABASE_URL` to managed PostgreSQL.
4. Install dependencies with:
   ```bash
   pip install -r requirements.txt
   ```
5. Run migrations:
   ```bash
   python manage.py migrate
   ```
6. Collect static files:
   ```bash
   python manage.py collectstatic --noinput
   ```
7. Start command:
   ```bash
   gunicorn productivity_tracker.wsgi:application
   ```

##  Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

##  License

This project is licensed under the MIT License - see the LICENSE file for details.

##  Acknowledgments

- Django framework and community
- Bootstrap for UI components
- Chart.js for data visualization
- FullCalendar for calendar functionality

##  Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the code comments

---

**Happy Productivity Tracking! **




