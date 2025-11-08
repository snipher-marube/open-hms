# Clinic HMS - Hospital Management System

![Django](https://img.shields.io/badge/Django-5.2.8-green)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.0%2B-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

A comprehensive, open-source Hospital Management System built with Django and TailwindCSS, designed for clinics and healthcare facilities to manage patients, appointments, inventory, and medical records efficiently.

## 🌟 Features

### 🏥 Core Modules
- **Patient Management** - Complete patient records with medical history
- **Appointment Scheduling** - Book, track, and manage doctor appointments
- **Inventory Management** - Medicine stock tracking with expiry alerts
- **Prescription System** - Digital prescriptions with medicine tracking
- **Billing & Payments** - Invoice generation and payment tracking
- **Medical Records** - Secure storage of patient medical history

### 📊 Advanced Features
- **Real-time Dashboard** - Analytics and key performance indicators
- **Inventory Alerts** - Low stock and expiry notifications
- **Professional Reporting** - Comprehensive analytics with PDF/Excel export
- **Role-based Access** - Secure multi-user system with permissions
- **Responsive Design** - Mobile-friendly interface

### 🔧 Technical Features
- **Modern UI** - Built with TailwindCSS for beautiful, responsive design
- **RESTful API** - AJAX endpoints for dynamic functionality
- **Data Export** - Export reports to PDF and Excel formats
- **Search & Filter** - Advanced search across all modules
- **Form Validation** - Robust client and server-side validation

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Django 5.2+
- SQLite (default) or PostgreSQL

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/clinic-hms.git
cd clinic-hms
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run migrations**
```bash
python manage.py migrate
```

5. **Create superuser**
```bash
python manage.py createsuperuser
```

6. **Load sample data (optional)**
```bash
python manage.py setup_default_data
```

7. **Run development server**
```bash
python manage.py runserver
```

Visit `http://localhost:8000` and login with your superuser credentials.

### Default Credentials
- Username: `admin`
- Password: `admin123`

## 📁 Project Structure

```
clinic-hms/
├── core/                 # Core app with base models and views
├── patients/            # Patient management
├── appointments/        # Appointment scheduling
├── inventory/           # Medicine inventory management
├── prescriptions/       # Prescription system
├── billing/            # Billing and payments
├── templates/          # HTML templates
│   ├── base.html       # Base template
│   ├── core/           # Core templates
│   └── [app_name]/     # App-specific templates
├── static/             # Static files (CSS, JS, images)
└── media/              # Uploaded media files
```

## 🛠️ Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Database Configuration
The system uses SQLite by default. For production, configure PostgreSQL in `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'hms_db',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 📊 Modules Overview

### Patient Management
- Complete patient profiles with demographic information
- Medical history and allergy tracking
- Emergency contact details
- Patient search and filtering
- Medical records management

### Appointment System
- Doctor scheduling and availability
- Appointment status tracking (scheduled, confirmed, completed, cancelled)
- Automated reminders (future enhancement)
- Doctor performance analytics

### Inventory Management
- Medicine stock tracking with batch numbers
- Expiry date monitoring and alerts
- Low stock notifications
- Supplier management
- Stock transaction history
- Automated stock deduction from prescriptions

### Prescription System
- Digital prescription creation
- Medicine dosage and frequency tracking
- Prescription history
- Integration with inventory for stock management

### Billing & Payments
- Invoice generation
- Multiple payment methods (cash, card, insurance, online)
- Payment tracking and history
- Outstanding balance management

### Reporting & Analytics
- Patient registration trends
- Appointment analytics
- Inventory reports
- Financial performance
- Medical statistics
- Export to PDF and Excel formats

## 🎨 Customization

### Adding New Modules
1. Create a new Django app: `python manage.py startapp new_module`
2. Add models in `new_module/models.py`
3. Create views in `new_module/views.py`
4. Add URLs in `new_module/urls.py`
5. Create templates in `templates/new_module/`
6. Register app in `settings.py`

### Styling Customization
The system uses TailwindCSS. Customize the design by:
- Modifying `base.html` for global changes
- Updating component classes in templates
- Adding custom CSS in `static/css/`

### Adding New Reports
1. Extend the `generate_report` function in `core/views.py`
2. Create report template in `templates/core/reports/`
3. Add chart configurations in the template
4. Update URLs and navigation

## 🔒 Security Features

- **User Authentication** - Django's built-in auth system
- **Role-based Permissions** - Different access levels for staff
- **CSRF Protection** - Built-in Django CSRF middleware
- **XSS Protection** - Template auto-escaping
- **SQL Injection Protection** - Django ORM
- **Secure File Uploads** - Validated file types and sizes

## 📈 Performance Optimization

- **Database Indexing** - Optimized queries with proper indexes
- **Template Caching** - Frequently accessed templates are cached
- **Static Files** - CDN-ready static file serving
- **Lazy Loading** - Images and heavy content loaded on demand
- **Pagination** - Large datasets are paginated

## 🚀 Deployment

### Production Checklist
- [ ] Set `DEBUG=False`
- [ ] Generate new `SECRET_KEY`
- [ ] Configure production database
- [ ] Set up static files serving
- [ ] Configure email backend
- [ ] Set up SSL certificate
- [ ] Configure allowed hosts
- [ ] Set up backup system
- [ ] Configure logging

### Deployment Options

**Docker (Recommended)**
```dockerfile
FROM python:3.11
# Add Dockerfile and docker-compose.yml
```

**Traditional Deployment**
```bash
python manage.py collectstatic
python manage.py migrate
gunicorn hms_project.wsgi:application
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings for functions and classes
- Write tests for new features
- Update documentation accordingly

## 📋 Roadmap

### Phase 1 (Completed)
- [x] Patient management system
- [x] Appointment scheduling
- [x] Basic inventory management
- [x] Prescription system
- [x] Basic reporting

### Phase 2 (In Progress)
- [ ] Laboratory module
- [ ] Radiology module
- [ ] Pharmacy module
- [ ] Advanced analytics
- [ ] Mobile app

### Phase 3 (Planned)
- [ ] Telemedicine integration
- [ ] AI-powered diagnostics
- [ ] IoT device integration
- [ ] Multi-language support
- [ ] Multi-tenant architecture

## 🐛 Troubleshooting

### Common Issues

**Database errors**
```bash
python manage.py makemigrations
python manage.py migrate
```

**Static files not loading**
```bash
python manage.py collectstatic
```

**Permission errors**
- Check file permissions in `media/` and `static/` directories
- Ensure the web server has write access

**Email configuration**
- Update email settings in `settings.py`
- Configure SMTP server for production

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Django](https://www.djangoproject.com/) - The web framework used
- [TailwindCSS](https://tailwindcss.com/) - CSS framework
- [Chart.js](https://www.chartjs.org/) - For beautiful charts
- [Heroicons](https://heroicons.com/) - For beautiful icons

## 📞 Support

- **Documentation**: [Read the Docs](https://clinic-hms.readthedocs.io/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/clinic-hms/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/clinic-hms/discussions)
- **Email**: support@clinic-hms.com

## 🌟 Show Your Support

If you find this project helpful, please give it a ⭐️ on GitHub!

---

**Built with ❤️ for the healthcare community**