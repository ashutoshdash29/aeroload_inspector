from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Aircraft(models.Model):
    name = models.CharField(max_length=100)
    registration = models.CharField(max_length=20, unique=True)
    aircraft_type = models.CharField(max_length=100, blank=True)
    max_takeoff_weight = models.FloatField(
        help_text="MTOW in kg",
        null=True, blank=True
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='aircraft'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.registration})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Aircraft'
        verbose_name_plural = 'Aircraft'


class LoadCase(models.Model):

    MANEUVER_CHOICES = [
        ('pull_up',   'Pull-Up'),
        ('push_over', 'Push-Over'),
        ('roll',      'Roll'),
        ('gust',      'Gust Load'),
        ('ground',    'Ground Load'),
        ('landing',   'Landing Impact'),
    ]

    FLIGHT_PHASE_CHOICES = [
        ('cruise',   'Cruise'),
        ('climb',    'Climb'),
        ('descent',  'Descent'),
        ('takeoff',  'Takeoff'),
        ('landing',  'Landing'),
    ]

    aircraft = models.ForeignKey(
        Aircraft,
        on_delete=models.CASCADE,
        related_name='load_cases'
    )
    name = models.CharField(max_length=200)
    maneuver_type = models.CharField(max_length=20, choices=MANEUVER_CHOICES)
    flight_phase = models.CharField(max_length=20, choices=FLIGHT_PHASE_CHOICES)

    # Load parameters
    load_factor_nz = models.FloatField(
        help_text="Vertical load factor (g)",
        validators=[MinValueValidator(-4.0), MaxValueValidator(9.0)]
    )
    speed_ktas = models.FloatField(help_text="Speed in knots TAS")
    altitude_ft = models.FloatField(help_text="Altitude in feet")

    # Status
    is_critical = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='load_cases'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ── computed properties ──────────────────────────────────────────
    @property
    def speed_ms(self):
        """Convert KTAS to m/s"""
        return round(self.speed_ktas * 0.5144, 2)

    @property
    def dynamic_pressure(self):
        """q = 0.5 × ρ × V²  (sea-level ISA, ρ = 1.225 kg/m³)"""
        return round(0.5 * 1.225 * self.speed_ms ** 2, 2)

    @property
    def severity_label(self):
        nz = abs(self.load_factor_nz)
        if nz >= 3.5:
            return 'HIGH'
        elif nz >= 2.0:
            return 'MEDIUM'
        return 'LOW'

    def __str__(self):
        return f"{self.name} | nz={self.load_factor_nz}g @ {self.speed_ktas}kt"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Load Case'
        verbose_name_plural = 'Load Cases'


class AnalysisReport(models.Model):

    STATUS_CHOICES = [
        ('pending',  'Pending'),
        ('complete', 'Complete'),
        ('flagged',  'Flagged — Needs Review'),
    ]

    load_case = models.OneToOneField(
        LoadCase,
        on_delete=models.CASCADE,
        related_name='report'
    )
    max_bending_moment = models.FloatField(help_text="Nm")
    max_shear_force    = models.FloatField(help_text="N")
    safety_factor      = models.FloatField(default=1.5)
    status             = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    analyst = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reports'
    )
    notes    = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_safe(self):
        """FAR 25 minimum safety factor is 1.5"""
        return self.safety_factor >= 1.5

    @property
    def margin_of_safety(self):
        """MoS = (SF / 1.5) - 1  — standard aerospace formula"""
        return round((self.safety_factor / 1.5) - 1, 3)

    def __str__(self):
        return f"Report: {self.load_case.name} [{self.status}]"

    class Meta:
        ordering = ['-created_at']