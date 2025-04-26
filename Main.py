# Workload Management System Implementation
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum, auto
import uuid
from datetime import datetime

class OrderStatus(Enum):
    PLACED = auto()
    WIP = auto()
    COMPLETE = auto()

class ProductType(Enum):
    VEG_PIZZA = "Veg Pizza"
    NV_PIZZA = "Non-Veg Pizza"
    SANDWICH = "Sandwich"
    BURGER = "Burger"
    DRINKS = "Drinks"

@dataclass
class Product:
    code: str
    description: str
    price: float
    product_type: ProductType

@dataclass
class OrderItem:
    product_code: str
    quantity: int
    toppings: List[str] = field(default_factory=list)
    price: float = 0.0

@dataclass
class Order:
    order_number: str
    items: List[OrderItem]
    status: OrderStatus = OrderStatus.PLACED
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    def update_status(self, new_status: OrderStatus):
        self.status = new_status
        if new_status == OrderStatus.COMPLETE:
            self.completed_at = datetime.now()

@dataclass
class Staff:
    id: str
    name: str
    skills: List[ProductType]  # Groups the staff belongs to
    logged_in: bool = False

    def can_handle_product(self, product_type: ProductType) -> bool:
        return product_type in self.skills

class WorkloadManagementSystem:
    def __init__(self):
        self.orders_queue: List[Order] = []
        self.staff_members: Dict[str, Staff] = {}
        self.products: Dict[str, Product] = {}
        self.product_group_mapping: Dict[ProductType, List[Staff]] = {}
        
        # Initialize with sample data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        # Create products
        products_data = [
            ("P001", "Margherita Pizza", 8.99, ProductType.VEG_PIZZA),
            ("P002", "Pepperoni Pizza", 10.99, ProductType.NV_PIZZA),
            ("S001", "Veg Sandwich", 5.99, ProductType.SANDWICH),
            ("B001", "Cheeseburger", 7.99, ProductType.BURGER),
            ("D001", "Soft Drink", 1.99, ProductType.DRINKS),
        ]
        
        for code, desc, price, p_type in products_data:
            self.products[code] = Product(code, desc, price, p_type)
        
        # Create staff
        staff_data = [
            ("S001", "Chandler", [ProductType.VEG_PIZZA, ProductType.BURGER]),
            ("S002", "Joey", [ProductType.VEG_PIZZA, ProductType.NV_PIZZA, ProductType.SANDWICH, ProductType.BURGER]),
            ("S003", "Rachel", [ProductType.NV_PIZZA]),
            ("S004", "Monica", [ProductType.SANDWICH]),
            ("S005", "Ross", [ProductType.DRINKS]),
        ]
        
        for id, name, skills in staff_data:
            self.staff_members[id] = Staff(id, name, skills)
        
        # Build product group mapping
        self._update_product_group_mapping()
    
    def _update_product_group_mapping(self):
        """Update which staff can handle which product types based on their skills and login status"""
        self.product_group_mapping = {pt: [] for pt in ProductType}
        
        for staff in self.staff_members.values():
            if staff.logged_in:
                for skill in staff.skills:
                    self.product_group_mapping[skill].append(staff)
    
    def staff_login(self, staff_id: str):
        """Staff logs into the system"""
        if staff_id in self.staff_members:
            self.staff_members[staff_id].logged_in = True
            self._update_product_group_mapping()
            return True
        return False
    
    def staff_logout(self, staff_id: str):
        """Staff logs out of the system"""
        if staff_id in self.staff_members:
            self.staff_members[staff_id].logged_in = False
            self._update_product_group_mapping()
            return True
        return False
    
    def place_order(self, items: List[Dict]) -> Order:
        """Create a new order and add it to the queue"""
        order_number = f"ORD{datetime.now().strftime('%d%m%Y')}{uuid.uuid4().hex[:3].upper()}"
        order_items = []
        
        for item in items:
            product_code = item.get('product_code')
            if product_code not in self.products:
                continue
                
            product = self.products[product_code]
            order_item = OrderItem(
                product_code=product_code,
                quantity=item.get('quantity', 1),
                toppings=item.get('toppings', []),
                price=product.price * item.get('quantity', 1)
            )
            order_items.append(order_item)
        
        if not order_items:
            raise ValueError("No valid items in order")
        
        order = Order(order_number, order_items)
        self.orders_queue.append(order)
        return order
    
    def process_orders(self):
        """Process orders in the queue (FIFO) and assign to available staff"""
        processed_orders = []
        
        for order in self.orders_queue[:]:  # Iterate over a copy
            if order.status != OrderStatus.PLACED:
                continue
                
            all_items_assigned = True
            
            for item in order.items:
                product = self.products[item.product_code]
                available_staff = self.product_group_mapping.get(product.product_type, [])
                
                if not available_staff:
                    all_items_assigned = False
                    print(f"No available staff for {product.product_type.value}")
                    break
            
            if all_items_assigned:
                order.update_status(OrderStatus.WIP)
                processed_orders.append(order)
                self.orders_queue.remove(order)
        
        return processed_orders
    
    def complete_order_item(self, order_number: str, product_code: str):
        """Mark an order item as complete and check if whole order is complete"""
        order = next((o for o in self.orders_queue if o.order_number == order_number), None)
        if not order:
            return False
        
        # In a real system, we'd track completion of individual items
        # For simplicity, we'll assume all items are completed together
        order.update_status(OrderStatus.COMPLETE)
        return True
    
    def get_available_products(self) -> List[Product]:
        """Get list of products that have at least one staff member available"""
        available_products = []
        
        for product in self.products.values():
            if self.product_group_mapping.get(product.product_type):
                available_products.append(product)
        
        return available_products
    
    def get_orders_by_status(self, status: OrderStatus) -> List[Order]:
        """Get orders filtered by status"""
        return [order for order in self.orders_queue if order.status == status]

# Example usage
if __name__ == "__main__":
    system = WorkloadManagementSystem()
    
    # Staff login
    system.staff_login("S001")  # Chandler logs in (Veg Pizza, Burger)
    system.staff_login("S004")  # Monica logs in (Sandwich)
    
    # Check available products
    available = system.get_available_products()
    print("Available products:")
    for product in available:
        print(f"- {product.description}")
    
    # Place an order
    order1_items = [
        {"product_code": "P001", "quantity": 2},  # Veg Pizza
        {"product_code": "S001", "quantity": 1},  # Sandwich
    ]
    order1 = system.place_order(order1_items)
    print(f"\nPlaced order {order1.order_number} with {len(order1.items)} items")
    
    # Process orders
    processed = system.process_orders()
    print(f"\nProcessed {len(processed)} orders")
    
    # Check order status
    orders_wip = system.get_orders_by_status(OrderStatus.WIP)
    print(f"\nOrders in WIP status: {len(orders_wip)}")
    
    # Complete order
    system.complete_order_item(order1.order_number, "P001")
    print(f"\nOrder {order1.order_number} status: {order1.status}")
