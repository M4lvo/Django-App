from django.db import models


class Product(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    Name = models.CharField(max_length=50)
    Quantity = models.IntegerField(default=0)
    Cost = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return self.Name + " -- " + str(self.Quantity)


class Purchase(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    Quantity = models.IntegerField()
    Date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} {}".format(self.Date, self.product.Name if self.product else "Deleted_Product")


class Sale(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    Quantity = models.IntegerField()
    Date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} {}".format(self.Date.date(), self.product.Name if self.product else "Deleted_Product")


class TotalCostP(models.Model):
    id = models.IntegerField(primary_key=True)
    Total_Cost = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'total_cost_p_v'


class TotalCostS(models.Model):
    id = models.IntegerField(primary_key=True)
    Total_Cost = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'total_cost_s_v'


class PurchaseSaleDiff(models.Model):
    Product_ID = models.IntegerField(primary_key=True)
    Difference = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'Purchase_Sale_Diff'


class PurchasedUnits(models.Model):
    Product_ID = models.IntegerField(primary_key=True)
    Total_Units = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'units_purchased'


class SoldUnits(models.Model):
    Product_ID = models.IntegerField(primary_key=True)
    Total_Units = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'units_sold'
