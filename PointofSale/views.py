from django.shortcuts import render
from .models import Product, Purchase, Sale, TotalCostP, TotalCostS, PurchaseSaleDiff, PurchasedUnits, SoldUnits
import datetime
from django.db.models import Sum
from django.http import HttpResponse
from xlwt import Workbook, easyxf

PRODUCT_ID = 0
PRODUCT_NAME = 1
PURCHASED_UNITS_INDEX = 1
SOLD_UNITS_INDEX = 1
PS_DIFF_INDEX = 1
PRODUCT_QUANTITY = 2
COLUMN_128 = 4690
COLUMN_75 = 2750
COLUMN_145 = 5312
COLUMN_100 = 3664
COLUMN_200 = 7326


def menu(request):
    return render(request, "menu.html",)


def purchase(request):
    all_purchase = Purchase.objects.all()
    all_cost = TotalCostP.objects.all()
    p_units = PurchasedUnits.objects.all()
    all_product = Product.objects.all()

    return render(request, "purchase.html", {'all_Purchases': dict(zip(all_purchase, all_cost)),
                                             'p_units': dict(zip(all_product, p_units)), })


def sale(request):
    all_sale = Sale.objects.all()
    all_cost = TotalCostS.objects.all()
    s_units = SoldUnits.objects.all()
    all_product = Product.objects.all()

    return render(request, "sale.html", {'all_Sales': dict(zip(all_sale, all_cost)),
                                         's_units': dict(zip(all_product, s_units)), })


def ireport(request):
    comb_list = []
    per_list = []

    all_product = Product.objects.values_list()
    p_units = PurchasedUnits.objects.values_list()
    s_units = SoldUnits.objects.values_list()
    ps_dff = PurchaseSaleDiff.objects.values_list()

    for i in range(0, len(all_product), 1):
        comb_list.append({'id': all_product[i][PRODUCT_ID],
                          'name': all_product[i][PRODUCT_NAME],
                          'p_units': p_units[i][PURCHASED_UNITS_INDEX],
                          's_units': s_units[i][SOLD_UNITS_INDEX],
                          'ps_diff': ps_dff[i][PS_DIFF_INDEX],
                          'current': all_product[i][PRODUCT_QUANTITY]})

    for i in range(0, len(all_product), 1):
        per_list.append({'name': all_product[i][PRODUCT_NAME],
                         'percent': (s_units[i][SOLD_UNITS_INDEX]/p_units[i][PURCHASED_UNITS_INDEX] if p_units[i][PURCHASED_UNITS_INDEX]!=0 else 0)*100})

    return render(request, "ireport.html", {'all_Product': comb_list,
                                            'all_Percent': per_list})


def preport(request):
    mindate = []
    maxdate = []

    for each in [Purchase.objects.order_by('Date')[0], Sale.objects.order_by('Date')[0]]:
        mindate.append(each.Date)

    for each in [Purchase.objects.order_by('Date')[Purchase.objects.count()-1],
                 Sale.objects.order_by('Date')[Sale.objects.count()-1]]:
        maxdate.append(each.Date)

    start = min(mindate)
    end = max(maxdate)

    return render(request, "preport.html", {'daterange': [start.date(), end.date()]})


def greport(request):
    # Retrieving dates from the URL
    date_from = datetime.datetime.strptime(request.GET['From'], "%Y-%m-%d")
    date_till = datetime.datetime.strptime(request.GET['Till'], "%Y-%m-%d")

    # Checking for valid date range
    if date_from <= date_till:

        # Retrieving all the sales in the date range
        sales = Sale.objects.filter(Date__range=(date_from, date_till + datetime.timedelta(days=1)))
        ids = [item.id for item in sales]
        sales_cost = TotalCostS.objects.filter(id__in=ids)

        # Retrieving all the purchases in the date range
        purchases = Purchase.objects.filter(Date__range=(date_from, date_till + datetime.timedelta(days=1)))
        idp = [item.id for item in purchases]
        purchases_cost = TotalCostP.objects.filter(id__in=idp)

        # Retrieving the Total_Sales_Income and Total_Purchase_Expense and Difference
        tsi = sales_cost.aggregate(Total_S=Sum('Total_Cost'))
        tpe = purchases_cost.aggregate(Total_P=Sum('Total_Cost'))

        # Difference
        diff = tsi['Total_S'] - tpe['Total_P']
        hol = diff > 0

        # Generating HttpResponse
        return render(request, "g_preport.html", {'SALES': dict(zip(sales, sales_cost)),
                                                  'PURCHASES': dict(zip(purchases, purchases_cost)),
                                                  'Total_PS': {**tsi, **tpe, 'diff': diff, 'hol': hol},
                                                  'Dates': {'from': date_from, 'before': date_till, },
                                                  })

    # If date range is invalid, i.e. the 'From' date is actually ahead of the 'Till' date:
    else:
        return render(request, "g_preport.html", {'error_message': "Invalid Date Range"})


def export_pos_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Salesreport.xls"'

    # Retrieving dates from the URL
    date_from = datetime.datetime.strptime(request.POST['From'], "%Y-%m-%d")
    date_till = datetime.datetime.strptime(request.POST['Till'], "%Y-%m-%d")

    # Retrieving all the sales in the date range
    sales = Sale.objects.filter(Date__range=(date_from, date_till + datetime.timedelta(days=1)))
    ids = [item.id for item in sales]
    sales_cost = TotalCostS.objects.filter(id__in=ids)
    all_sales = dict(zip(sales, sales_cost))

    # Retrieving all the purchases in the date range
    purchases = Purchase.objects.filter(Date__range=(date_from, date_till + datetime.timedelta(days=1)))
    idp = [item.id for item in purchases]
    purchases_cost = TotalCostP.objects.filter(id__in=idp)
    all_purchase = dict(zip(purchases, purchases_cost))

    # Retrieving the Total_Sales_Income and Total_Purchase_Expense and Difference
    tsi = sales_cost.aggregate(Total_S=Sum('Total_Cost'))
    tpe = purchases_cost.aggregate(Total_P=Sum('Total_Cost'))

    # Difference
    diff = tsi['Total_S'] - tpe['Total_P']
    hol = diff > 0

    # Writing new excel book
    row_count = inc(0)
    col_count = inc(0, 5)

    book = Workbook()
    sheet = book.add_sheet('Sheet 1')
    sheet.col(1).width = COLUMN_75
    sheet.col(2).width = COLUMN_200
    sheet.col(3).width = COLUMN_145
    sheet.col(5).width = COLUMN_100

    # Declaring styles
    heading_style = easyxf(
        'font:bold True, color white, Height 300;''pattern:pattern solid_fill, fore_colour indigo;'
        'borders: left thick, right thick, top thick, bottom thick;''alignment:vertical centre, horizontal centre')
    row_heading_style = easyxf('font:bold True;')
    result_style = easyxf('font:bold True;''alignment:vertical centre, horizontal centre;')
    diff_style = easyxf('font:bold True;''alignment:vertical centre, horizontal centre;'
                        'pattern:pattern solid_fill, fore_colour light_green;') if hol else \
        easyxf('font:bold True, color white;''alignment:vertical centre, horizontal centre;'
               'pattern:pattern solid_fill, fore_colour dark_red;')

    # Writing main heading
    sheet.write_merge(next(row_count), next(row_count), 0, 6,
                      'Generated Sales Report from ' + date_from.strftime("%d / %m / %Y") +
                      ' till ' + date_till.strftime("%d / %m / %Y"),
                      heading_style)
    next(row_count)

    # Writing Sales heading
    sheet.write_merge(next(row_count), next(row_count), 0, 1,
                      'Sales', heading_style)
    next(row_count)

    # Writing first header row
    cur_row = next(row_count)
    sheet.row(cur_row).set_cell_text(next(col_count), 'S-ID', row_heading_style)
    sheet.row(cur_row).set_cell_text(next(col_count), 'Product-ID', row_heading_style)
    sheet.row(cur_row).set_cell_text(next(col_count), 'Product Name', row_heading_style)
    sheet.row(cur_row).set_cell_text(next(col_count), 'Date-Time', row_heading_style)
    sheet.row(cur_row).set_cell_text(next(col_count), 'Quantity', row_heading_style)
    sheet.row(cur_row).set_cell_text(next(col_count), 'Price', row_heading_style)

    # Writing Sale Entries
    for key, value in all_sales.items():
        cur_row = next(row_count)
        sheet.row(cur_row).set_cell_number(next(col_count), key.id)
        sheet.row(cur_row).set_cell_number(next(col_count), key.product.id)
        sheet.row(cur_row).set_cell_text(next(col_count), key.product.Name)
        sheet.row(cur_row).set_cell_text(next(col_count), key.Date.strftime("%d / %m / %Y %H:%M:%S"))
        sheet.row(cur_row).set_cell_number(next(col_count), key.Quantity)
        sheet.row(cur_row).set_cell_number(next(col_count), value.Total_Cost)
    sheet.write_merge(next(row_count), next(row_count), 4, 5,
                      'Total Income: '+str(tsi['Total_S']), result_style)
    next(row_count)

    # Writing Purchases heading
    sheet.write_merge(next(row_count), next(row_count), 0, 1,
                      'Purchases', heading_style)
    next(row_count)

    # Writing first header row
    cur_row = next(row_count)
    sheet.row(cur_row).set_cell_text(next(col_count), 'P-ID', row_heading_style)
    sheet.row(cur_row).set_cell_text(next(col_count), 'Product-ID', row_heading_style)
    sheet.row(cur_row).set_cell_text(next(col_count), 'Product Name', row_heading_style)
    sheet.row(cur_row).set_cell_text(next(col_count), 'Date-Time', row_heading_style)
    sheet.row(cur_row).set_cell_text(next(col_count), 'Quantity', row_heading_style)
    sheet.row(cur_row).set_cell_text(next(col_count), 'Price', row_heading_style)

    # Writing Purchase Entries
    for key, value in all_purchase.items():
        cur_row = next(row_count)
        sheet.row(cur_row).set_cell_number(next(col_count), key.id)
        sheet.row(cur_row).set_cell_number(next(col_count), key.product.id)
        sheet.row(cur_row).set_cell_text(next(col_count), key.product.Name)
        sheet.row(cur_row).set_cell_text(next(col_count), key.Date.strftime("%d / %m / %Y %H:%M:%S"))
        sheet.row(cur_row).set_cell_number(next(col_count), key.Quantity)
        sheet.row(cur_row).set_cell_number(next(col_count), value.Total_Cost)
    sheet.write_merge(next(row_count), next(row_count), 4, 5,
                      'Total Expenses: '+str(tpe['Total_P']), result_style)

    # Writing final calculated difference
    sheet.write_merge(next(row_count), next(row_count), 4, 5, 'Difference: '+str(diff), diff_style)

    # Saving and returning excel workbook
    book.save(response)
    return response


def newtransaction(request):
    all_product = Product.objects.all()
    return render(request, 'trans.html', {'all_products': all_product})


def newproduct(request):
    return render(request, 'product.html')


def addproduct(request):
    if request.POST:
        name = request.POST['Product_Name']
        cost = request.POST['Cost']
        newp = Product(Name=name, Cost=cost)
        newp.save()
        return render(request, 'menu.html', {'message': "Product stored successfully"})
    else:
        return render(request, 'menu.html')


def addtrans(request):
    if request.POST:
        p = Product.objects.get(id=request.POST['Product'])
        q = request.POST['Quantity']
        if request.POST['type'] == 'P':
            newp = Purchase(product=p, Quantity=q)
            newp.save()
        elif request.POST['type'] == 'S':
            news = Sale(product=p, Quantity=q)
            news.save()
        return render(request, 'menu.html', {'message': "Transaction completed"})
    else:
        return render(request, 'menu.html')


def inc(start, end=None):
    n = start
    if end:
        while True:
            yield n
            n += 1
            if n > end:
                n = start
    else:
        while True:
            yield n
            n += 1
