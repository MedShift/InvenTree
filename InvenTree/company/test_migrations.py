"""
Tests for the company model database migrations
"""

from django_test_migrations.contrib.unittest_case import MigratorTestCase


class TestManufacturerField(MigratorTestCase):
    """
    Tests for migration 0019 which migrates from old 'manufacturer_name' field to new 'manufacturer' field
    """

    migrate_from = ('company', '0018_supplierpart_manufacturer')
    migrate_to = ('company', '0019_auto_20200413_0642')

    def prepare(self):
        """
        Prepare the database by adding some test data 'before' the change:

        - Part object
        - Company object (supplier)
        - SupplierPart object
        """
        
        Part = self.old_state.apps.get_model('part', 'part')
        Company = self.old_state.apps.get_model('company', 'company')
        SupplierPart = self.old_state.apps.get_model('company', 'supplierpart')

        # Create an initial part
        part = Part.objects.create(
            name='Screw',
            description='A single screw'
        )

        # Create a company to act as the supplier
        supplier = Company.objects.create(
            name='Supplier',
            description='A supplier of parts',
            is_supplier=True,
            is_customer=False,
        )

        # Add some SupplierPart objects
        SupplierPart.objects.create(
            part=part,
            supplier=supplier,
            SKU='SCREW.001',
            manufacturer_name='ACME',
        )

        SupplierPart.objects.create(
            part=part,
            supplier=supplier,
            SKU='SCREW.002',
            manufacturer_name='Zero Corp'
        )

        self.assertEqual(Company.objects.count(), 1)

    def test_company_objects(self):
        """
        Test that the new companies have been created successfully
        """

        # Two additional company objects should have been created
        Company = self.new_state.apps.get_model('company', 'company')
        self.assertEqual(Company.objects.count(), 3)

        # The new company/ies must be marked as "manufacturers"
        acme = Company.objects.get(name='ACME')
        self.assertTrue(acme.is_manufacturer)

        SupplierPart = self.new_state.apps.get_model('company', 'supplierpart')
        parts = SupplierPart.objects.filter(manufacturer=acme)
        self.assertEqual(parts.count(), 1)
        part = parts.first()

        # Checks on the SupplierPart object
        self.assertEqual(part.manufacturer_name, 'ACME')
        self.assertEqual(part.manufacturer.name, 'ACME')
