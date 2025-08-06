
class PaginationMixin:
    """
    Mixin para paginación inteligente con ventana deslizante.
    Uso: class MiVista(PaginationMixin, ListView)
    """
    pagination_window_size = 3  # 3 páginas a cada lado (7 en total)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_obj = context.get('page_obj')
        
        if page_obj:
            current_page = page_obj.number
            total_pages = page_obj.paginator.num_pages
            window = self.pagination_window_size
            
            if total_pages <= (window * 2) + 1:
                context['custom_page_range'] = range(1, total_pages + 1)
            elif current_page <= window:
                context['custom_page_range'] = range(1, (window * 2) + 2)
            elif current_page >= total_pages - window:
                context['custom_page_range'] = range(total_pages - (window * 2), total_pages + 1)
            else:
                context['custom_page_range'] = range(current_page - window, current_page + window + 1)
        
        return context