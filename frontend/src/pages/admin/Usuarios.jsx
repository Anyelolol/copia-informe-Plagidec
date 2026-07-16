import { useEffect, useState } from 'react'
import { adminService } from '../../services/adminService'
import styles from './Admin.module.css'

export default function Usuarios() {
  const [usuarios, setUsuarios] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    adminService.listarUsuarios()
      .then(setUsuarios)
      .catch(e => setError(e.response?.data?.error || 'Error'))
      .finally(() => setLoading(false))
  }, [])

  const desactivar = async (uid, nombre) => {
    if (!confirm(`¿Desactivar a ${nombre}?`)) return
    try {
      await adminService.eliminarUsuario(uid)
      setUsuarios(prev => prev.map(u => u.uid === uid ? { ...u, activo: false } : u))
    } catch (e) {
      alert(e.response?.data?.error || 'Error')
    }
  }

  return (
    <div>
      <h1 className={styles.title}>Usuarios</h1>
      {loading && <span className="spinner" />}
      {error && <p className="error-msg">{error}</p>}
      {!loading && usuarios.length > 0 && (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Nombre</th>
                <th>Email</th>
                <th>Rol</th>
                <th>Activo</th>
                <th>Último acceso</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {usuarios.map(u => (
                <tr key={u.uid}>
                  <td style={{ color: 'var(--text-muted)' }}>{u.uid}</td>
                  <td>{u.nombre} {u.apellido}</td>
                  <td style={{ color: 'var(--text-muted)' }}>{u.email}</td>
                  <td><span className={`badge badge-${u.rol === 'admin' ? 'warning' : 'info'}`}>{u.rol}</span></td>
                  <td><span className={`badge badge-${u.activo ? 'success' : 'danger'}`}>{u.activo ? 'Sí' : 'No'}</span></td>
                  <td style={{ color: 'var(--text-muted)', fontSize: 12 }}>{u.ultimo_acceso ? new Date(u.ultimo_acceso).toLocaleString() : '—'}</td>
                  <td>
                    {u.activo && u.rol !== 'admin' && (
                      <button className="btn-danger" style={{ padding: '4px 10px', fontSize: 12 }} onClick={() => desactivar(u.uid, u.nombre)}>
                        Desactivar
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
