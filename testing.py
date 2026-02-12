order_query = f' ORDER BY HasPermit ASC'
order_query = order_query[:10]+'c.'+order_query[10:]
print(order_query)