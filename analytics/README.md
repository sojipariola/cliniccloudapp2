# Analytics Module - Business Intelligence for Healthcare SaaS

## Overview
The Analytics module provides comprehensive business intelligence and data visualization capabilities exclusively for **Professional** and **Enterprise** subscription tiers. It enables executive decision-making through intelligent data diagrams, KPIs, and actionable insights.

## Access Control

### Subscription Requirements
- **Free Trial**: ❌ No access
- **Starter Plan**: ❌ No access
- **Professional Plan**: ✅ Full access
- **Enterprise Plan**: ✅ Full access

### User Requirements
- Must be logged in
- Must have `admin` role or be superuser
- Organization must have Professional or Enterprise subscription

### Access Decorator
```python
from analytics.decorators import admin_or_analytics_access

@admin_or_analytics_access
def my_analytics_view(request):
    # Your analytics logic here
    pass
```

## Features

### 1. Main Analytics Dashboard
**URL**: `/analytics/` or `/analytics/dashboard/`
**View**: `analytics_dashboard`

**Key Performance Indicators**:
- Total Patients (with 30-day growth)
- Monthly Appointments (current month + upcoming)
- Clinical Records (total + monthly)
- Lab Results (total + pending)
- Active Users (admins breakdown)
- Completed Appointments (30-day count)
- Revenue Metrics (90-day totals, averages)
- Active Patients (90-day engagement)

**Features**:
- Interactive navigation to detailed analytics
- Visual KPI cards with gradients
- Quick insights section
- Upgrade encouragement for lower tiers

### 2. Executive Summary
**URL**: `/analytics/executive/`
**View**: `executive_summary`

**Metrics**:
- Patient Growth (month-over-month %)
- Monthly Revenue (with growth rate)
- Appointment Completion Rate
- Active Users (30-day)
- Year-to-Date Revenue

**Strategic Insights**:
- Automated analysis of growth patterns
- Performance recommendations
- Action items based on KPIs
- Trend analysis with contextual advice

**Perfect For**:
- Board presentations
- Quarterly reviews
- Executive briefings
- Strategic planning

### 3. Patient Analytics
**URL**: `/analytics/patients/`
**View**: `patient_analytics`

**Visualizations**:
- Patient Growth Chart (12-month line chart)
- Age Distribution (doughnut chart + table)
- Demographics breakdown

**Data Points**:
- Total patient count
- New patient acquisition trends
- Age range distribution (0-18, 19-35, 36-50, 51-65, 65+)

**Use Cases**:
- Marketing campaign planning
- Service line development
- Capacity planning
- Demographic targeting

### 4. Appointment Analytics
**URL**: `/analytics/appointments/`
**View**: `appointment_analytics`

**Visualizations**:
- Monthly Appointment Trends (bar chart)
- Status Distribution (pie chart)
- Appointments by Day of Week (bar chart)
- Top Appointment Types (table with percentages)

**Metrics**:
- Total appointments
- Scheduled vs. completed vs. cancelled
- Daily/weekly patterns
- Appointment type popularity

**Insights**:
- Identify busy days for staffing
- Optimize scheduling windows
- Reduce no-show rates
- Balance appointment types

### 5. Revenue Analytics
**URL**: `/analytics/revenue/`
**View**: `revenue_analytics`

**Visualizations**:
- Monthly Revenue Trends (line chart)
- Top 10 Patients by Revenue (table)
- Payment Methods Distribution (table)

**Metrics**:
- Total revenue (all-time)
- Average payment amount
- Payment count
- Revenue by patient
- Currency/method breakdown

**Business Intelligence**:
- Identify high-value patients
- Track revenue trends
- Forecast future revenue
- Optimize pricing strategies

### 6. User Activity Analytics
**URL**: `/analytics/users/`
**View**: `user_activity_analytics`

**Visualizations**:
- Daily Activity Timeline (30-day line chart)
- Top Event Types (table)
- Most Active Users (leaderboard)

**Metrics**:
- Total system events
- Event type distribution
- User engagement levels
- Activity patterns

**Use Cases**:
- Monitor system adoption
- Identify training needs
- Track feature usage
- Assess user engagement

## Technical Architecture

### Models

#### AnalyticsEvent
```python
class AnalyticsEvent(models.Model):
    tenant = ForeignKey(Tenant)           # Multi-tenant isolation
    event_type = CharField(max_length=64) # Type of event
    user_id = IntegerField(null=True)     # User who triggered event
    timestamp = DateTimeField()           # When it happened
    metadata = JSONField()                # Additional data (JSON)
```

**Event Types**:
- `login`, `logout`
- `patient_view`, `patient_create`, `patient_edit`
- `appointment_create`, `appointment_edit`, `appointment_cancel`
- `clinical_record_create`, `clinical_record_view`
- `lab_result_create`, `lab_result_view`
- `document_upload`
- `referral_create`
- `payment_received`
- `report_generated`
- `other`

**Indexes**:
- `(tenant, event_type, timestamp)` - Fast event aggregation
- `(tenant, user_id, timestamp)` - User activity queries

### Data Sources

The analytics module aggregates data from:
- `patients.Patient` - Patient demographics and growth
- `appointments.Appointment` - Scheduling and utilization
- `clinical_records.ClinicalRecord` - Clinical activity
- `labs.LabResult` - Laboratory metrics
- `billing.Payment` - Financial performance
- `users.CustomUser` - User activity and engagement
- `analytics.AnalyticsEvent` - System events

### Security

#### Multi-Tenant Isolation
All queries are automatically filtered by `request.user.tenant`:
```python
Patient.objects.filter(tenant=tenant)
Appointment.objects.filter(tenant=tenant)
```

#### Role-Based Access
Only administrators can access analytics:
```python
def is_admin(user):
    return user.is_superuser or getattr(user, 'role', None) == 'admin'
```

#### Subscription Enforcement
Automatic redirect to upgrade page if plan doesn't support analytics:
```python
if tenant.plan not in ('professional', 'enterprise'):
    messages.error(request, "Analytics requires Professional or Enterprise plan")
    return redirect('view_plans')
```

## Visualization Technology

### Chart.js 4.4.0
All charts use Chart.js for interactive, responsive visualizations:

**Chart Types Used**:
- Line Charts: Trends over time (growth, revenue, activity)
- Bar Charts: Comparisons (monthly data, day-of-week)
- Pie/Doughnut Charts: Distributions (status, age groups)

**Features**:
- Responsive design (mobile-friendly)
- Interactive tooltips
- Smooth animations
- Gradient backgrounds
- Custom color schemes

### CSS Styling
Modern, professional design with:
- Gradient headers
- Card-based layouts
- Grid system (CSS Grid)
- Shadow effects
- Responsive breakpoints
- Color-coded KPIs

## Usage Examples

### For Administrators

**Scenario 1: Monthly Performance Review**
1. Navigate to `/analytics/executive/`
2. Review key metrics: patient growth, revenue, completion rate
3. Read automated insights and recommendations
4. Click through to detailed sections for deep dives

**Scenario 2: Marketing Campaign Planning**
1. Navigate to `/analytics/patients/`
2. Review 12-month patient growth chart
3. Analyze age distribution to target demographics
4. Use insights to design targeted campaigns

**Scenario 3: Operational Optimization**
1. Navigate to `/analytics/appointments/`
2. Review day-of-week distribution
3. Identify peak days (e.g., Tuesday/Wednesday)
4. Adjust staffing accordingly

**Scenario 4: Financial Planning**
1. Navigate to `/analytics/revenue/`
2. Review monthly revenue trends
3. Identify top revenue-generating patients
4. Forecast future revenue based on trends

### For Developers

**Add Custom Analytics Event**:
```python
from analytics.models import AnalyticsEvent

# Track a custom event
AnalyticsEvent.objects.create(
    tenant=request.user.tenant,
    event_type='custom_event',
    user_id=request.user.id,
    metadata={'action': 'special_action', 'value': 123}
)
```

**Create New Analytics View**:
```python
from analytics.decorators import admin_or_analytics_access
from django.shortcuts import render

@admin_or_analytics_access
def my_custom_analytics(request):
    tenant = request.user.tenant
    # Your analytics logic here
    context = {
        'data': my_data,
        'chart_labels': json.dumps(labels),
        'chart_data': json.dumps(data)
    }
    return render(request, 'analytics/my_custom.html', context)
```

**Add to URLs**:
```python
# config/urls.py
path('analytics/custom/', my_custom_analytics, name='my_custom_analytics'),
```

## Database Migrations

After installing or modifying the analytics module:

```bash
# Create migrations for model changes
python manage.py makemigrations analytics

# Apply migrations
python manage.py migrate analytics
```

## Performance Optimization

### Query Optimization
- Use `select_related()` and `prefetch_related()` for foreign keys
- Add `.only()` or `.defer()` for large datasets
- Use `.values()` for aggregations
- Implement pagination for large result sets

### Caching Strategy
```python
from django.core.cache import cache

# Cache expensive queries
cache_key = f'analytics_patients_{tenant.id}'
data = cache.get(cache_key)
if not data:
    data = expensive_query()
    cache.set(cache_key, data, 3600)  # Cache for 1 hour
```

### Database Indexes
Already implemented on:
- `AnalyticsEvent.tenant` + `event_type` + `timestamp`
- `AnalyticsEvent.tenant` + `user_id` + `timestamp`

## Testing

### Unit Tests
```python
from django.test import TestCase
from analytics.models import AnalyticsEvent
from tenants.models import Tenant

class AnalyticsEventTest(TestCase):
    def test_event_creation(self):
        tenant = Tenant.objects.create(name='Test Clinic')
        event = AnalyticsEvent.objects.create(
            tenant=tenant,
            event_type='patient_view',
            user_id=1
        )
        self.assertEqual(event.event_type, 'patient_view')
```

### Access Control Tests
```python
def test_analytics_requires_professional_plan(self):
    # Create tenant with starter plan
    tenant = Tenant.objects.create(name='Starter Clinic', plan='starter')
    user = CustomUser.objects.create(username='admin', tenant=tenant, role='admin')
    
    self.client.force_login(user)
    response = self.client.get('/analytics/')
    
    # Should redirect to upgrade page
    self.assertRedirects(response, '/billing/plans/')
```

## Troubleshooting

### Issue: "Analytics features are only available for Professional and Enterprise plans"
**Solution**: Upgrade tenant plan:
```python
tenant = Tenant.objects.get(name='Your Clinic')
tenant.plan = 'professional'  # or 'enterprise'
tenant.save()
```

### Issue: "You must be an administrator to access analytics"
**Solution**: Update user role:
```python
user = CustomUser.objects.get(username='youruser')
user.role = 'admin'
user.save()
```

### Issue: Charts not displaying
**Solution**: Check browser console for JavaScript errors. Ensure Chart.js is loaded:
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
```

### Issue: No data showing in analytics
**Solution**: Create some test events:
```python
from analytics.models import AnalyticsEvent
from datetime import timedelta
from django.utils import timezone

# Create sample events
for i in range(30):
    AnalyticsEvent.objects.create(
        tenant=tenant,
        event_type='patient_view',
        user_id=1,
        timestamp=timezone.now() - timedelta(days=i)
    )
```

## Future Enhancements

### Planned Features
- [ ] Export analytics reports to PDF/Excel
- [ ] Email scheduled reports to admins
- [ ] Custom date range selection
- [ ] Drill-down capabilities
- [ ] Predictive analytics (ML-based forecasting)
- [ ] Comparison to industry benchmarks
- [ ] Custom dashboard builder
- [ ] Real-time analytics (WebSocket updates)
- [ ] Mobile app analytics views
- [ ] API endpoints for external tools

### Integration Opportunities
- Google Analytics integration
- Tableau/PowerBI connectors
- Slack/Teams notifications
- Email alert triggers
- FHIR analytics endpoints

## API Documentation (Future)

When API endpoints are added:

```
GET /api/analytics/kpis/
GET /api/analytics/patients/
GET /api/analytics/appointments/
GET /api/analytics/revenue/
POST /api/analytics/events/
```

## Support & Resources

- **Documentation**: `/analytics/` dashboard includes help links
- **Training**: Contact support for analytics training sessions
- **Custom Reports**: Enterprise customers can request custom analytics
- **Data Export**: Contact support for bulk data exports

## Compliance & Privacy

### HIPAA Compliance
- All analytics data is tenant-isolated
- No PHI is exposed in URLs or logs
- Analytics events do not store sensitive patient data
- All access is audited via `audit_logs` module

### Data Retention
- Analytics events retained for 2 years by default
- Configure retention in `config/settings.py`:
```python
ANALYTICS_RETENTION_DAYS = 730  # 2 years
```

### Privacy Considerations
- User IDs stored as integers (not usernames/emails)
- Metadata should NOT contain PHI
- All queries filtered by tenant (no cross-tenant data leaks)

---

**Version**: 1.0
**Last Updated**: January 2026
**Module Status**: ✅ Production Ready
**Subscription Requirement**: Professional or Enterprise
