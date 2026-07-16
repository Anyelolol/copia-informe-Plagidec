import { Link } from 'react-router-dom'
import { useHistorial } from '../hooks/useHistorial'
import ScoreBadge from '../components/ScoreBadge'
import styles from './Historial.module.css'

export default function Historial() {
  const { historial, loading, error, cargar } = useHistorial()

  return (
    <div>
      <div className={styles.header}>
        <h1 className={styles.title}>Historial de evaluaciones</h1>
        <button className="btn-ghost" onClick={cargar}>↻ Actualizar</button>
      </div>

      {loading && <span className="spinner" />}
      {error && <p className="error-msg">{error}</p>}

      {!loading && historial.length === 0 && (
        <p style={{ color: 'var(--text-muted)', textAlign: 'center', marginTop: 40 }}>Sin evaluaciones aún.</p>
      )}

      {historial.length > 0 && (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table>
            <thead>
              <tr>
                <th>Eval #</th>
                <th>Doc #</th>
                <th>Tipo</th>
                <th>Score</th>
                <th>IA detectada</th>
                <th>Estado</th>
                <th>Fecha</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {historial.map(e => (
                <tr key={e.eid}>
                  <td>#{e.eid}</td>
                  <td>#{e.did}</td>
                  <td style={{ color: 'var(--text-muted)', fontSize: 12 }}>{e.tipo_evaluacion}</td>
                  <td><ScoreBadge score={e.score_similitud} /></td>
                  <td>
                    {e.resultado_json?.ia_detection
                      ? <span className={`badge badge-${e.resultado_json.ia_detection.is_ai ? 'danger' : 'success'}`}>
                          {e.resultado_json.ia_detection.is_ai ? 'Sí' : 'No'}
                        </span>
                      : <span style={{ color: 'var(--text-muted)' }}>—</span>}
                  </td>
                  <td>
                    <span className={`badge badge-${e.estado === 'completado' ? 'success' : e.estado === 'error' ? 'danger' : 'info'}`}>
                      {e.estado}
                    </span>
                  </td>
                  <td style={{ color: 'var(--text-muted)', fontSize: 12 }}>{new Date(e.creado_en).toLocaleDateString()}</td>
                  <td><Link to={`/historial/${e.eid}`}><button className="btn-ghost" style={{ padding: '4px 12px', fontSize: 12 }}>Ver</button></Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
