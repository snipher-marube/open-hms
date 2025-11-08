# Contributing to Clinic HMS

Thank you for your interest in contributing to Clinic HMS! We welcome contributions from the community and are grateful for your help in making this project better.

## 🎯 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Contributions](#making-contributions)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Bug Reports](#bug-reports)
- [Feature Requests](#feature-requests)
- [Community](#community)

## 📜 Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct:

- Be respectful and inclusive
- Exercise consideration and respect in your speech and actions
- Attempt collaboration before conflict
- Refrain from demeaning, discriminatory, or harassing behavior
- Be mindful of your surroundings and fellow participants

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of Django framework

### First Time Contributors

If you're new to open source or this project, check out our [Good First Issues](https://github.com/yourusername/clinic-hms/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22) to get started.

## 💻 Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Clone your fork locally
git clone https://github.com/snipher-marube/open-hms.git
cd open-hms

# Add upstream remote
git remote add upstream https://github.com/snipher-marube/open-hms.git
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# Run migrations
python manage.py migrate

# Create superuser (for testing)
python manage.py createsuperuser

# Load sample data
python manage.py setup_default_data
```

### 3. Run Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` to verify the setup.

## 🔧 Making Contributions

### Branch Naming Convention

Use descriptive branch names:

- `feature/description` - For new features
- `bugfix/description` - For bug fixes
- `hotfix/description` - For critical production fixes
- `docs/description` - For documentation updates
- `refactor/description` - For code refactoring

### Example Workflow

```bash
# Sync with upstream
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/patient-search-enhancement

# Make your changes
# ... code, test, document ...

# Commit changes
git add .
git commit -m "feat: enhance patient search with filters and autocomplete

- Add advanced search filters for patient records
- Implement autocomplete for medicine names
- Improve search performance with database indexes
- Add unit tests for search functionality"

# Push to your fork
git push origin feature/patient-search-enhancement
```

## 📝 Pull Request Process

### 1. Before Submitting

- [ ] Ensure your code follows our [coding standards](#coding-standards)
- [ ] Run the test suite and add tests for new functionality
- [ ] Update documentation for new features or changes
- [ ] Check that your code passes all CI checks
- [ ] Rebase your branch on the latest main branch

### 2. PR Description Template

```markdown
## Description
Brief description of the changes

## Related Issue
Fixes #(issue number)

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update
- [ ] Code refactoring

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Screenshots (if applicable)

## Checklist
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code where necessary
- [ ] I have updated the documentation
- [ ] My changes generate no new warnings
```

### 3. Code Review

- PRs require at least one maintainer approval
- Address review comments promptly
- Keep PRs focused and manageable in size
- Be responsive to feedback and questions

## 🎨 Coding Standards

### Python/Django Code

```python
# Good example
from django.db import models
from django.utils import timezone


class Patient(models.Model):
    """Model representing a patient in the system."""
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    phone = models.CharField(max_length=15)
    
    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        """Calculate patient's age."""
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < 
            (self.date_of_birth.month, self.date_of_birth.day)
        )


def get_patient_statistics(start_date, end_date):
    """
    Get patient statistics for the given date range.
    
    Args:
        start_date: Start date for statistics
        end_date: End date for statistics
        
    Returns:
        dict: Patient statistics
    """
    # Implementation here
    pass
```

### HTML/Templates

```html
<!-- Good example -->
{% extends 'base.html' %}
{% load static %}

{% block title %}Patient List - HMS{% endblock %}

{% block content %}
<div class="max-w-6xl mx-auto">
    <div class="flex justify-between items-center mb-6">
        <h1 class="text-2xl font-bold text-gray-800">Patients</h1>
        <a href="{% url 'patient-create' %}" 
           class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md transition duration-200">
            Add Patient
        </a>
    </div>
    
    <!-- Patient list content -->
</div>
{% endblock %}
```

### JavaScript

```javascript
// Good example
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('patient-search');
    const resultsDiv = document.getElementById('search-results');
    
    /**
     * Handle patient search input
     */
    function handleSearchInput() {
        const query = searchInput.value.trim();
        
        if (query.length < 2) {
            resultsDiv.style.display = 'none';
            return;
        }
        
        // Search implementation
        performSearch(query);
    }
    
    searchInput.addEventListener('input', debounce(handleSearchInput, 300));
});
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test patients

# Run with coverage
coverage run manage.py test
coverage report
coverage html  # Generate HTML report
```

### Writing Tests

```python
# tests/test_patient_models.py
from django.test import TestCase
from django.utils import timezone
from patients.models import Patient


class PatientModelTest(TestCase):
    """Test cases for Patient model."""
    
    def setUp(self):
        """Set up test data."""
        self.patient = Patient.objects.create(
            first_name='John',
            last_name='Doe',
            date_of_birth=timezone.now().date().replace(year=1990),
            phone='+1234567890'
        )
    
    def test_patient_creation(self):
        """Test patient creation."""
        self.assertEqual(self.patient.first_name, 'John')
        self.assertEqual(self.patient.last_name, 'Doe')
        self.assertTrue(self.patient.age > 30)
    
    def test_patient_str_representation(self):
        """Test string representation."""
        self.assertEqual(str(self.patient), 'John Doe')
```

## 📚 Documentation

### Code Documentation

- Use docstrings for all functions, classes, and methods
- Follow Google-style docstring format
- Document complex algorithms and business logic
- Keep comments up-to-date with code changes

### User Documentation

- Update README.md for significant changes
- Document new features in appropriate sections
- Include screenshots for UI changes
- Update API documentation if applicable

## 🐛 Bug Reports

When reporting bugs, please include:

### Bug Report Template

```markdown
## Description
Clear and concise description of the bug.

## Steps to Reproduce
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior
What you expected to happen.

## Actual Behavior
What actually happened.

## Screenshots
If applicable, add screenshots to help explain.

## Environment
- OS: [e.g., Windows, macOS, Linux]
- Browser: [e.g., Chrome, Safari, Firefox]
- Version: [e.g., 1.0.0]

## Additional Context
Add any other context about the problem.
```

## 💡 Feature Requests

We welcome feature requests! Please use the template:

### Feature Request Template

```markdown
## Problem Statement
Clear description of the problem this feature would solve.

## Proposed Solution
Description of the proposed solution.

## Alternative Solutions
Any alternative solutions or features considered.

## Additional Context
Add any other context, mockups, or examples.
```

## 🏷️ Issue Labels

We use the following labels to categorize issues:

- `bug` - Something isn't working
- `enhancement` - New feature or improvement
- `documentation` - Documentation updates
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `question` - Further information is requested
- `wontfix` - This will not be worked on

## 👥 Community

### Getting Help

- **GitHub Discussions**: For questions and discussions
- **GitHub Issues**: For bug reports and feature requests
- **Email**: For sensitive security issues

### Recognition

Contributors will be recognized in:
- Project README
- Release notes
- Contributor hall of fame

### Becoming a Maintainer

After consistent quality contributions, you may be invited to become a maintainer. Maintainers are expected to:

- Review and merge pull requests
- Triage issues
- Help guide project direction
- Mentor new contributors

## 📄 License

By contributing, you agree that your contributions will be licensed under the same [MIT License](LICENSE) that covers the project.

## 🙏 Acknowledgments

Thank you to all our contributors who have helped make Clinic HMS better!

---

**Happy Contributing! 🎉**

If you have any questions, don't hesitate to ask in our [GitHub Discussions](https://github.com/yourusername/clinic-hms/discussions).