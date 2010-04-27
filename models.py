#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import datetime

from django.db import models

from rapidsms.models import Contact
from rapidsms.contrib.locations.models import Location

class Waypoint(Location):
    last_updated = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=160)
    location = models.ForeignKey(Location)

class Origin(Waypoint):

    def __unicode__(self):
        return "%s" % (self.name)

class Destination(Waypoint):

    class Meta:
        verbose_name = "Delivery destination"

    def __unicode__(self):
        return "%s" % (self.name)

class School(Destination):
    address
    km_to_DEO
    GPS_south
    GPS_east
    contact
    code

class Commodity(models.Model):
    STATUS_CHOICES = (
        ('PL', 'pallets'),
        ('TM', 'Tons (metric)'),
        ('KG', 'Kilograms'),
        ('BX', 'Boxes'),
        ('TB', 'Tiny boxes'),
        ('BL', 'Bales'),
        ('LT', 'Liters'),
        ('CN', 'Containers'),
        ('DS', 'Doses'),
    )
    name = models.CharField(max_length=160)
    slug = models.CharField(max_length=6, unique=True)

    volume = models.CharField(max_length=160)
    weight = models.CharField(max_length=160)

    unit = models.CharField(max_length=2, choices=UNIT_CHOICES)

    def __unicode__(self):
        return self.name

class Cargo(models.model):
    commodity = models.ForeignKey(Commodity)
    quantity = models.CharField(max_length=160)
    shipment = models.ForeignKey('Shipment')

    def __unicode__(self):
        return "%s pallets of %s to %s" % (self.quantity, self.commodity, self.shipment.destination)

class Shipment(models.Model):
    STATUS_CHOICES = (
        ('P', 'Planned shipment'),
        ('T', 'Shipment in transit'),
        ('D', 'Completed shipment'),
    )
    status = models.CharField(max_length=2, choices=STATUS_CHOICES)
    cargo = models.ForeignKey(Cargo)

    origin = models.ForeignKey(Destination)
    destination = models.ForeignKey(Destination)

    created = models.DateTimeField(default=datetime.datetime.utcnow)
    modified = models.DateTimeField(default=datetime.datetime.utcnow)

    shipping_date = models.DateTimeField()
    expected_delivery_date = models.DateTimeField()
    actual_delivery_date = models.DateTimeField()

    def __unicode__(self):
        return "Shipment of %s pallets of %s to %s" % (self.cargo.quantity, self.cargo.commodity, self.destination)

    class Meta:
        verbose_name = "Shipment"

    @classmethod
    def active(cls):
        return cls.objects.exclude(status="delivered")

class Tracking(models.Model):
    shipment = models.ForeignKey(Shipment)
    updated = models.DateTimeField(default=datetime.datetime.utcnow)
    tracked_by = models.ForeignKey(Contact)
    waypoint = models.ForeignKey(Waypoint)
