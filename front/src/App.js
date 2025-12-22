import { useEffect, useState } from 'react';
import io from 'socket.io-client';
import { PieChart, Pie, Cell, Legend, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import './App.css';

// 원형 차트 색상
const COLORS = ['#28a745', '#dc3545'];
const DEVICE_COLORS = ['#f59e0b', '#ef4444', '#3b82f6', '#8b5cf6'];

function App() {
  const [stats, setStats] = useState({
    total_count: 0,
    overall: {
      normal_car_count: 0,
      defect_car_count: 0,
      defect_rate: 0,
      defect_log_count: 0
    },
    sensor: {
      defect_car_count: 0,
      defect_rate: 0,
      defect_log_count: 0,
      by_device: {}
    },
    camera: {
      defect_car_count: 0,
      defect_rate: 0,
      defect_log_count: 0
    }
  });

  const [alerts, setAlerts] = useState([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    // 초기 데이터 받아오기 (REST API)
    const fetchInitialData = async () => {
      try {
        const response = await fetch('http://localhost:5000/dashboard/summary');
        const data = await response.json();
        console.log('초기 데이터:', data);
        setStats(data);
      } catch (error) {
        console.error('초기 데이터 로드 실패:', error);
        addAlert('❌ 초기 데이터를 불러올 수 없습니다', 'error');
      }
    };

    fetchInitialData();

    // WebSocket 연결
    const socket = io('http://localhost:5000', {
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 5
    });

    // 연결 성공
    socket.on('connect', () => {
      console.log('서버 연결됨');
      setConnected(true);
    });

    // 초기 통계 수신
    socket.on('stats', (data) => {
      console.log('초기 통계 수신:', data);
      setStats(data);
    });

    // 통계 업데이트
    socket.on('stats_update', (data) => {
      console.log('통계 업데이트:', data);
      setStats(data);
    });

    // 센서 불량
    socket.on('sensor_defect', (data) => {
      console.log('센서 불량:', data);
      addAlert(`⚠️ 센서 불량 감지: ${data.device}`, 'error');
    });

    // 카메라 불량
    socket.on('camera_defect', (data) => {
      console.log('카메라 불량:', data);
      addAlert('⚠️ 외관 불량 감지됨', 'error');
    });

    // 차량 추가
    socket.on('car_added', (data) => {
      console.log('새 차량:', data);
      addAlert('🚗 새 차량 추가됨', 'success');
    });

    // 연결 끊김
    socket.on('disconnect', () => {
      console.log('서버 연결 끊김');
      setConnected(false);
    });

    // 에러
    socket.on('error', (error) => {
      console.error('Socket 에러:', error);
      addAlert('❌ 연결 오류', 'error');
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  const addAlert = (message, type) => {
    const id = Date.now();
    setAlerts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setAlerts(prev => prev.filter(a => a.id !== id));
    }, 5000);
  };

  // 전체 통계 원형 차트 데이터
  const overallChartData = [
    { name: '정상 차량', value: stats.overall.normal_car_count },
    { name: '불량 차량', value: stats.overall.defect_car_count }
  ];

  // 센서 불량 차량 원형 차트 데이터
  const sensorCarChartData = [
    { name: '정상 차량', value: stats.total_count - stats.sensor.defect_car_count },
    { name: '불량 차량', value: stats.sensor.defect_car_count }
  ];

  // 센서 장치별 원형 차트 데이터 (건수)
  const sensorChartData = Object.entries(stats.sensor.by_device)
    .filter(([_, info]) => info.defect_log_count > 0)
    .map(([device, info]) => ({
      name: device,
      value: info.defect_log_count
    }));

  // 센서 장치별 차량 원형 차트 데이터
  const sensorDeviceCarChartData = Object.entries(stats.sensor.by_device)
    .filter(([_, info]) => info.defect_car_count > 0)
    .map(([device, info]) => ({
      name: device,
      value: info.defect_car_count
    }));

  // 외관 불량 차량 원형 차트 데이터
  const cameraCarChartData = [
    { name: '정상 차량', value: stats.total_count - stats.camera.defect_car_count },
    { name: '불량 차량', value: stats.camera.defect_car_count }
  ];

  // 센서 불량 비율 (전체 불량 중 센서 불량)
  const sensorComparisonChartData = [
    { name: '센서 불량 차량', value: stats.sensor.defect_car_count },
    { name: '기타 불량 차량', value: stats.overall.defect_car_count - stats.sensor.defect_car_count }
  ];

  // 외관 불량 비율 (전체 불량 중 외관 불량)
  const cameraComparisonChartData = [
    { name: '외관 불량 차량', value: stats.camera.defect_car_count },
    { name: '기타 불량 차량', value: stats.overall.defect_car_count - stats.camera.defect_car_count }
  ];

  return (
    <div className="App">
      <header className="header">
        <div className="header-content">
          <h1>🚗 자동차 검사 실시간 대시보드</h1>
          <p className="header-subtitle">센서 및 외관 검사 통계</p>
        </div>
        <div className="connection-status">
          <span className={`status ${connected ? 'connected' : 'disconnected'}`}>
            <span className="status-dot"></span>
            {connected ? '연결됨' : '연결 끊김'}
          </span>
        </div>
      </header>

      <div className="alerts-container">
        {alerts.map(alert => (
          <div key={alert.id} className={`alert alert-${alert.type}`}>
            {alert.message}
          </div>
        ))}
      </div>

      <div className="dashboard">
        {/* 전체 통계 카드 */}
        <div className="card summary-card">
          <div className="card-header">
            <h2>📊 전체 검사 현황</h2>
          </div>
          
          <div className="card-content">
            <div className="chart-container">
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={overallChartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={2}
                    dataKey="value"
                  >
                    {overallChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => `${value}대`} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="stat-grid">
              <div className="stat-box">
                <label>총 차량 수</label>
                <div className="stat-value large">{stats.total_count}</div>
              </div>
              <div className="stat-box">
                <label>정상 차량</label>
                <div className="stat-value success">{stats.overall.normal_car_count}</div>
              </div>
              <div className="stat-box">
                <label>불량 차량</label>
                <div className="stat-value error">{stats.overall.defect_car_count}</div>
              </div>
              <div className="stat-box">
                <label>전체 불량률</label>
                <div className="stat-value error">{stats.overall.defect_rate}%</div>
              </div>
              <div className="stat-box">
                <label>전체 불량 건수</label>
                <div className="stat-value error">{stats.overall.defect_log_count}</div>
              </div>
            </div>
          </div>
        </div>

        {/* 센서 검사 카드 */}
        <div className="card sensor-card">
          <div className="card-header">
            <h2>🔧 센서 검사</h2>
            <span className="card-subtitle">센서 검사 데이터</span>
          </div>

          <div className="card-content">
            {/* 전체 불량 vs 센서 불량 도넛 */}
            <div className="chart-container">
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={sensorComparisonChartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={2}
                    dataKey="value"
                  >
                    {sensorComparisonChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => `${value}대`} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="stat-row">
              <div className="stat-cell">
                <label>불량 차량</label>
                <div className="value error">{stats.sensor.defect_car_count}대</div>
              </div>
              <div className="stat-cell">
                <label>불량률</label>
                <div className="value error">{stats.sensor.defect_rate}%</div>
              </div>
              <div className="stat-cell">
                <label>불량 건수</label>
                <div className="value error">{stats.sensor.defect_log_count}건</div>
              </div>
            </div>

            {/* 장치별 불량 */}
            <div className="section">
              <h3>장치별 상세 분석</h3>
              
              {sensorChartData.length > 0 && (
                <div className="chart-container small">
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={sensorChartData} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                      <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                      <YAxis tick={{ fontSize: 12 }} />
                      <Tooltip formatter={(value) => `${value}건`} />
                      <Bar 
                        dataKey="value" 
                        fill="#3b82f6" 
                        radius={[6, 6, 0, 0]}
                        maxBarSize={40}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}

              <div className="device-list">
                {Object.keys(stats.sensor.by_device).length > 0 ? (
                  Object.entries(stats.sensor.by_device).map(([device, info], idx) => (
                    <div key={device} className="device-item">
                      <div className="device-header">
                        <div className="device-color" style={{ backgroundColor: DEVICE_COLORS[idx % DEVICE_COLORS.length] }}></div>
                        <span className="device-name">{device}</span>
                      </div>
                      <div className="device-stats">
                        <div className="device-stat">
                          <span className="label">차량 불량</span>
                          <span className="value">{info.defect_car_count}대</span>
                        </div>
                        <div className="device-stat">
                          <span className="label">차량 비율</span>
                          <span className="value">{info.car_defect_rate}%</span>
                        </div>
                        <div className="device-stat">
                          <span className="label">불량 건수</span>
                          <span className="value">{info.defect_log_count}건</span>
                        </div>
                        <div className="device-stat">
                          <span className="label">건수 비율</span>
                          <span className="value">{info.log_defect_rate}%</span>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="no-data">불량 데이터 없음 ✓</p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* 카메라 검사 카드 */}
        <div className="card camera-card">
          <div className="card-header">
            <h2>📷 외관 검사</h2>
            <span className="card-subtitle">카메라 외관 검사 데이터</span>
          </div>

          <div className="card-content">
            {/* 전체 불량 vs 외관 불량 도넛 */}
            <div className="chart-container">
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={cameraComparisonChartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={2}
                    dataKey="value"
                  >
                    {cameraComparisonChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => `${value}대`} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="stat-row">
              <div className="stat-cell">
                <label>불량 차량</label>
                <div className="value error">{stats.camera.defect_car_count}대</div>
              </div>
              <div className="stat-cell">
                <label>불량률</label>
                <div className="value error">{stats.camera.defect_rate}%</div>
              </div>
              <div className="stat-cell">
                <label>불량 건수</label>
                <div className="value error">{stats.camera.defect_log_count}건</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
