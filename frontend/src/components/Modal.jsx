import '../styles/modal.css'

function Modal({ open, title, description, confirmLabel = 'Confirm', danger, onConfirm, onCancel, loading }) {
  if (!open) return null

  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal-card animate-scale-in" onClick={(e) => e.stopPropagation()}>
        <h3>{title}</h3>
        {description && <p>{description}</p>}
        <div className="modal-actions">
          <button className="btn-outline modal-btn" onClick={onCancel} disabled={loading}>
            Cancel
          </button>
          <button
            className={(danger ? 'btn-danger' : 'btn-gradient') + ' modal-btn'}
            onClick={onConfirm}
            disabled={loading}
          >
            {loading ? <span className="spinner" /> : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  )
}

export default Modal