from rest_framework import serializers, status
from .models import ExpenseBill, BillItem
from django.db.models import Sum


class BillItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillItem
        fields = '__all__'
        extra_kwargs = {'bill':{'required':False}}
        read_only_fields = ['final_amount']


class ExpenseManagerSerializer(serializers.ModelSerializer):
    bill_item = BillItemSerializer(many=True)
    class Meta:
        model = ExpenseBill
        fields = '__all__'
        read_only_fields = ['total_spends']

    def create(self, validated_data):
        bill_items = validated_data.pop('bill_item')
        bill = super().create(validated_data)
        try:
            for item in bill_items:
                holders = item.pop('holders')
                item['bill'] = bill.id
                new_item = BillItemSerializer(data=item)
                new_item.is_valid(raise_exception=True)
                new = new_item.save()
                for user in holders:
                    new.holders.add(user)
                new.save()
            total_amount = bill.bill_item.all().aggregate(
                total_amount= Sum('final_amount'))['total_amount']
            bill.total_spends = total_amount + bill.tip 
            bill.save()
        except Exception as e:
            bill.delete()
            raise serializers.ValidationError(str(e))
        return bill
    
    
    