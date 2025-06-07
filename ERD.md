# Entity Relationship Diagram (ERD)

## Entities and Relationships:

---

### 1. `accounts.User` (Extends Django's `AbstractUser`)
   - **Fields:**
     - `username` (from AbstractUser)
     - `password` (from AbstractUser)
     - `email` (from AbstractUser)
     - `first_name` (from AbstractUser)
     - `last_name` (from AbstractUser)
     - `role` (CharField: admin, stock_manager, sales)
     - `phone_number` (CharField, nullable)
   - **Relationships:**
     - `InventoryAdjustment` (One-to-Many): A user can create multiple inventory adjustments. (ForeignKey `created_by` in `InventoryAdjustment`)
     - `Order` (One-to-Many, as `created_by`): A user can create multiple orders. (ForeignKey `created_by` in `Order`)
     - `Order` (One-to-Many, as `updated_by`): A user can update multiple orders. (ForeignKey `updated_by` in `Order`)
     - `SalesReport` (One-to-Many): A user can generate multiple sales reports. (ForeignKey `generated_by` in `SalesReport`)

---

### 2. `products.Category`
   - **Fields:**
     - `name` (CharField)
     - `description` (TextField, nullable)
   - **Relationships:**
     - `Product` (One-to-Many): A category can have multiple products. (ForeignKey `category` in `Product`)

---

### 3. `products.Product`
   - **Fields:**
     - `name` (CharField, **unique**)
     - `cost_price` (DecimalField)
     - `selling_price` (DecimalField)
     - `description` (TextField, nullable)
   - **Relationships:**
     - `Category` (Many-to-One): A product belongs to one category.
     - `Supplier` (Many-to-One, nullable): A product can be supplied by one supplier.
     - `ProductImage` (One-to-Many): A product can have multiple images. (ForeignKey `product` in `ProductImage`)
     - `ProductVariant` (One-to-Many): A product can have multiple variants. (ForeignKey `product` in `ProductVariant`)
     - `TopSellingProduct` (One-to-Many): A product can appear in multiple top-selling product lists. (ForeignKey `product` in `TopSellingProduct`)

---

### 4. `products.ProductImage`
   - **Fields:**
     - `image` (ImageField)
     - `is_primary` (BooleanField)
   - **Relationships:**
     - `Product` (Many-to-One): An image belongs to one product.

---

### 5. `suppliers.Supplier`
   - **Fields:**
     - `name` (CharField)
     - `contact_person` (CharField)
     - `email` (EmailField)
     - `phone_number` (CharField)
     - `address` (TextField, nullable)
   - **Relationships:**
     - `Product` (One-to-Many, as `products`): A supplier can supply multiple products. (ForeignKey `supplier` in `Product`)

---

### 6. `inventory.Size`
   - **Fields:**
     - `name` (CharField)
   - **Relationships:**
     - `ProductVariant` (One-to-Many): A size can be used for multiple product variants. (ForeignKey `size` in `ProductVariant`)

---

### 7. `inventory.Color`
   - **Fields:**
     - `name` (CharField)
     - `color_code` (CharField, nullable)
   - **Relationships:**
     - `ProductVariant` (One-to-Many): A color can be used for multiple product variants. (ForeignKey `color` in `ProductVariant`)

---

### 8. `inventory.ProductVariant`
   - **Fields:**
     - `quantity` (PositiveIntegerField)
     - `reorder_level` (PositiveIntegerField)
   - **Constraints:**
     - `unique_together = ('product', 'size', 'color')`
   - **Relationships:**
     - `Product` (Many-to-One): A variant belongs to one product.
     - `Size` (Many-to-One): A variant has one size.
     - `Color` (Many-to-One): A variant has one color.
     - `InventoryAdjustment` (One-to-Many, as `adjustments`): A variant can have multiple inventory adjustments. (ForeignKey `variant` in `InventoryAdjustment`)
     - `OrderItem` (One-to-Many): A product variant can be part of multiple order items. (ForeignKey `product_variant` in `OrderItem`)

---

### 9. `inventory.InventoryAdjustment`
   - **Fields:**
     - `adjustment_type` (CharField: incoming, outgoing, adjustment)
     - `quantity` (IntegerField)
     - `notes` (TextField, nullable)
   - **Relationships:**
     - `ProductVariant` (Many-to-One): An adjustment is for one product variant.
     - `User` (Many-to-One, `accounts.User`, nullable): An adjustment is created by one user.

---

### 10. `orders.Customer`
    - **Fields:**
      - `name` (CharField)
      - `email` (EmailField, nullable)
      - `phone_number` (CharField)
      - `address` (TextField, nullable)
    - **Relationships:**
      - `Order` (One-to-Many, as `orders`): A customer can have multiple orders. (ForeignKey `customer` in `Order`)

---

### 11. `orders.Order`
    - **Fields:**
      - `order_date` (DateTimeField, auto_now_add)
      - `status` (CharField: pending, processing, awaiting_payment, shipped, delivered, cancelled)
      - `notes` (TextField, nullable)
    - **Relationships:**
      - `Customer` (Many-to-One): An order belongs to one customer.
      - `User` (Many-to-One, `accounts.User`, as `created_by`, nullable): An order is created by one user.
      - `User` (Many-to-One, `accounts.User`, as `updated_by`, nullable): An order is updated by one user.
      - `OrderItem` (One-to-Many, as `items`): An order can have multiple items. (ForeignKey `order` in `OrderItem`)

---

### 12. `orders.OrderItem`
    - **Fields:**
      - `quantity` (PositiveIntegerField)
      - `price` (DecimalField) - Price at the time of order
    - **Relationships:**
      - `Order` (Many-to-One): An order item belongs to one order.
      - `ProductVariant` (Many-to-One): An order item refers to one product variant.

---

### 13. `dashboard.SalesReport`
    - **Fields:**
      - `report_type` (CharField: daily, weekly, monthly)
      - `date_from` (DateField)
      - `date_to` (DateField)
      - `total_sales` (DecimalField)
      - `total_orders` (PositiveIntegerField)
    - **Relationships:**
      - `User` (Many-to-One, `accounts.User`, as `generated_by`, nullable): A sales report is generated by one user.
      - `TopSellingProduct` (One-to-Many, as `top_products`): A sales report can list multiple top-selling products. (ForeignKey `report` in `TopSellingProduct`)

---

### 14. `dashboard.TopSellingProduct`
    - **Fields:**
      - `total_quantity` (PositiveIntegerField)
      - `total_sales` (DecimalField)
    - **Relationships:**
      - `SalesReport` (Many-to-One): This record belongs to one sales report.
      - `Product` (Many-to-One): This record refers to one product.

---

**Key Relationship Types Used:**
*   **One-to-Many:** One record in a table can be associated with multiple records in another table. (e.g., One `Product` can have many `ProductImage`s). Indicated by `ForeignKey` on the "many" side.
*   **Many-to-One:** Multiple records in a table can be associated with one record in another table. (e.g., Many `Product`s can belong to one `Category`). This is the other side of a One-to-Many, also defined by `ForeignKey`.
*   **Many-to-Many:** (Not explicitly shown as a direct Django field in the provided models, but `ProductVariant` acts as an intermediary for a conceptual Many-to-Many between `Product`, `Size`, and `Color`).

This ERD should give you a good overview of your database schema.
