# Management-app
## Key Features Implemented:

1. **Order Management**:
   - Order creation with unique order numbers
   - Order status tracking (Placed → WIP → Complete)
   - Handling multi-item orders

2. **Staff Management**:
   - Staff login/logout functionality
   - Skill-based group mapping
   - Availability tracking

3. **Product Management**:
   - Product catalog with types
   - Availability based on staff skills and login status

4. **Queue Management**:
   - FIFO order processing
   - Auto-assignment to appropriate staff groups
   - Handling of orders with unavailable products

5. **Business Rules**:
   - Products only available if staff from their group is logged in
   - Orders split to multiple groups when containing multiple items
   - Status updates through order lifecycle

The implementation follows the requirements from the PDF, including the specific use cases and user stories mentioned. The system can be extended with additional features like:
- More detailed order item tracking
- Consolidation station logic
- Delivery management
- Reporting and analytics
