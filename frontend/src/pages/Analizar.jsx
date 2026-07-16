import { useState, useEffect } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { documentoService } from '../services/documentoService'
import { plagiarismService } from '../services/plagiarismService'
import ScoreBadge from '../components/ScoreBadge'
import styles from './Analizar.module.css'

export default function Analizar() {
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const [docs, setDocs] = useState([])
  const [form, setForm] = useState({ did: params.get('did') || '', referencia: '', tipo_evaluacion: 'similitud_semantica' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [resultado, setResultado] = useState(null)

  useEffect(() => {
    documentoService.listar().then(setDocs).catch(() => {})
  }, [])

  const onChange = e => setForm(p => ({ ...p, [e.target.name]: e.target.value }))

  const onSubmit = async e => {
    e.preventDefault()
    if (!form.did) { setError('Selecciona un documento'); return }
    setError('')
    setLoading(true)
    setResultado(null)
    try {
      const r = await plagiarismService.check(parseInt(form.did), form.referencia, form.tipo_evaluacion)
      setResultado(r)
    } catch (e) {
      setError(e.response?.data?.error || 'Error al analizar')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1 className={styles.title}>Nueva evaluación</h1>

      <div className={styles.grid}>
        <div className="card">
          <form onSubmit={onSubmit} className={styles.form}>
            <label>Documento
              <select name="did" value={form.did} onChange={onChange} required>
                <option value="">— Seleccionar —</option>
                {docs.map(d => (
                  <option key={d.did} value={d.did}>{d.nombre_original} (#{d.did})</option>
                ))}
              </select>
            </label>

            <label>Tipo de evaluación
              <select name="tipo_evaluacion" value={form.tipo_evaluacion} onChange={onChange}>
                <option value="similitud_semantica">Similitud semántica</option>
                <option value="deteccion_ia">Detección IA</option>
              </select>
            </label>

            <label>Texto de referencia <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}>(opcional)</span>
              <textarea name="referencia" value={form.referencia} onChange={onChange} rows={6} placeholder="Pega aquí el texto original para comparar..." />
            </label>

            {error && <p className="error-msg">{error}</p>}

            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? <><span className="spinner" style={{ marginRight: 8 }} /> Procesando…</> : 'Analizar'}
            </button>
          </form>
        </div>

        {resultado && (
          <div className={styles.resultado}>
            <div className="card" style={{ marginBottom: 16 }}>
              <div className={styles.scoreRow}>
                <div>
                  <div className={styles.scoreLabel}>Score de similitud</div>
                  <div className={styles.scoreBig}><ScoreBadge score={resultado.score_similitud} /></div>
                </div>
                {resultado.ia_detection && (
                  <div>
                    <div className={styles.scoreLabel}>Detección IA</div>
                    <div className={styles.scoreBig}>
                      <span className={`badge badge-${resultado.ia_detection.is_ai ? 'danger' : 'success'}`}>
                        {resultado.ia_detection.is_ai ? 'IA detectada' : 'No IA'}
                      </span>
                    </div>
                  </div>
                )}
                <button className="btn-ghost" style={{ marginLeft: 'auto' }} onClick={() => navigate(`/historial/${resultado.eid}`)}>
                  Ver detalle →
                </button>
              </div>
            </div>

            {resultado.segmentos?.length > 0 && (
              <div className="card">
                <h3 className={styles.secTitle}>Segmentos plagiados ({resultado.segmentos.length})</h3>
                <div className={styles.segments}>
                  {resultado.segmentos.map((s, i) => (
                    <div key={i} className={styles.segment}>
                      <span className="badge badge-danger" style={{ marginBottom: 4 }}>{Math.round((s.score_similitud || 0) * 100)}%</span>
                      <p>{s.texto_segmento}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
