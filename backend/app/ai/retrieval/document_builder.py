from app.db.models.product import Product

class DocumentBuilder:
    @staticmethod
    def build_product_document(product: Product, category_name: str) -> str:
        """
        Constructs a highly dense text representation of a product to feed into the embedding model.
        This rich document ensures semantic searches can match on brands, tags, and categories.
        """
        parts = []
        parts.append(f"Product Name: {product.name}")
        
        if product.brand:
            parts.append(f"Brand: {product.brand}")
            
        parts.append(f"Category: {category_name}")
        
        if product.description:
            parts.append(f"Description: {product.description}")
            
        return " | ".join(parts)
