from rest_framework import serializers
from core.models import Product, Category, Cart, CartItem, Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    products = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='shop:product-detail'
    )
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'products', 'products_count',)
        read_only_fields = ('id', 'count',)

    def get_products_count(self, obj):
        """Counts the number of products in a category."""
        counter = Product.objects.filter(categories=obj).count()
        return counter


class ProductCategorySerializer(serializers.ModelSerializer):
    """
    Nested product serializer in CategorySerializer.
    """
    class Meta:
        model = Category
        fields = ('id', 'name',)


class ProductSerializer(serializers.ModelSerializer):
    categories = ProductCategorySerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created', 'is_available')

    def create(self, validated_data):
        """
        Create or get existing category.
        """
        categories = validated_data.pop('categories', [])
        product = Product.objects.create(**validated_data)
        for category in categories:
            category_object, created = Category.objects.get_or_create(**category)

            product.categories.add(category_object)

        return product


class ProductOrderItemSerializer(serializers.ModelSerializer):
    """
    Nested product serializer in OrderItemSerializer.
    """
    class Meta:
        model = Product
        fields = ('id', 'name', 'price')
        read_only_fields = ('id', 'name', 'price')


class CartItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'quantity')

    def create(self, validated_data):
        """
        Checks if product is available and adds it to user cart.
        """
        product = Product.objects.get(pk=validated_data['product'].pk)
        if not product.is_available:
            raise serializers.ValidationError('Sorry, this product is not available')
        if validated_data['product'].quantity < validated_data['quantity']:
            raise serializers.ValidationError('Sorry, this quantity is not available!')
        cart, created = Cart.objects.get_or_create(user=self.context['request'].user)
        return CartItem.objects.create(cart=cart, **validated_data)


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True)
    user = serializers.StringRelatedField()

    class Meta:
        model = Cart
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True}
        }


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductOrderItemSerializer()

    class Meta:
        model = OrderItem
        fields = ('product', 'quantity')


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ('id', 'user', 'order_items', 'total_price', 'delivery_status', 'created_at', 'updated_at')
        read_only_fields = fields

    def get_total_price(self, obj):
        """
        Count total price of order.
        """
        order_items = OrderItem.objects.filter(order=obj.pk)
        total = 0
        for order_item in order_items:
            total += (order_item.product.price * order_item.quantity)
        return total

    def create(self, validated_data):
        """
        Checks if user cart exist, then creates order and adds products from cart.
        """
        try:
            cart = Cart.objects.get(user=self.context['request'].user)
        except Exception as e:
            error = {'message': ",".join(e.args) if len(e.args) > 0 else 'Unknown Error'}
            raise serializers.ValidationError(error)
        order = Order.objects.create(user=self.context['request'].user)
        for cart_item in cart.cart_items.all():
            OrderItem.objects.create(product=cart_item.product, quantity=cart_item.quantity, order=order)
            cart_item.product.quantity -= cart_item.quantity
            cart_item.product.save()
        cart.delete()
        return order


class OrderUpdateSerializer(OrderSerializer):

    class Meta:
        model = Order
        fields = ('id', 'user', 'order_items', 'total_price', 'delivery_status', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'order_items', 'total_price', 'created_at', 'updated_at')


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to recipes."""

    class Meta:
        model = Product
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': 'True'}}

