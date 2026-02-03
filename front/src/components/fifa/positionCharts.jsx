import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

const PositionCharts = ({ inputSequence, selectedResult }) => {
  const inputData =
    inputSequence?.map((point) => ({
      time: point.time,
      x: point.x,
      y: point.y,
    })) || [];

  const matchData =
    selectedResult?.matchCoordinates.map((point) => ({
      time: point.time,
      x: point.x,
      y: point.y,
    })) || [];

  const hasData = inputData.length > 0 || matchData.length > 0;

  if (!hasData) {
    return (
      <div className="card glass-card">
        <div className="card-header">
          <h5 className="card-title mb-0">Position Analysis</h5>
        </div>
        <div className="card-body">
          <div className="d-flex align-items-center justify-content-center py-5">
            <p className="text-muted mb-0">
              Select a sequence to view position analysis charts
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="card glass-card">
      <div className="card-header">
        <h5 className="card-title mb-0">Position Analysis</h5>
      </div>
      <div className="card-body">
        <div className="row g-4">
          {/* Input Sequence Chart */}
          <div className="col-lg-6">
            <h6 className="fw-medium mb-3 d-flex align-items-center gap-2">
              <div
                className="rounded-circle bg-primary"
                style={{ width: "12px", height: "12px" }}
              />
              Input Sequence
            </h6>
            <div style={{ height: "256px" }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={inputData}
                  margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
                >
                  <CartesianGrid stroke="#e2e8f0" strokeDasharray="3 3" />
                  <XAxis
                    dataKey="time"
                    label={{
                      value: "Time",
                      position: "insideBottom",
                      offset: -5,
                    }}
                    stroke="#64748b"
                    fontSize={12}
                  />
                  <YAxis
                    domain={[0, 100]}
                    label={{
                      value: "Position",
                      angle: -90,
                      position: "insideLeft",
                    }}
                    stroke="#64748b"
                    fontSize={12}
                  />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="x"
                    name="X Position"
                    stroke="#0ea5e9"
                    strokeWidth={2}
                    dot={{ fill: "#0ea5e9", r: 4 }}
                    activeDot={{ r: 6 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="y"
                    name="Y Position"
                    stroke="#06b6d4"
                    strokeWidth={2}
                    dot={{ fill: "#06b6d4", r: 4 }}
                    activeDot={{ r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Selected Match Chart */}
          <div className="col-lg-6">
            <h6 className="fw-medium mb-3 d-flex align-items-center gap-2">
              <div
                className="rounded-circle bg-warning"
                style={{ width: "12px", height: "12px" }}
              />
              Matched Sequence
              {selectedResult && (
                <span className="fw-normal text-muted small">
                  ({selectedResult.teams})
                </span>
              )}
            </h6>
            <div style={{ height: "256px" }}>
              {matchData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={matchData}
                    margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
                  >
                    <CartesianGrid stroke="#e2e8f0" strokeDasharray="3 3" />
                    <XAxis
                      dataKey="time"
                      label={{
                        value: "Time",
                        position: "insideBottom",
                        offset: -5,
                      }}
                      stroke="#64748b"
                      fontSize={12}
                    />
                    <YAxis
                      domain={[0, 100]}
                      label={{
                        value: "Position",
                        angle: -90,
                        position: "insideLeft",
                      }}
                      stroke="#64748b"
                      fontSize={12}
                    />
                    <Tooltip />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="x"
                      name="X Position"
                      stroke="#f97316"
                      strokeWidth={2}
                      dot={{ fill: "#f97316", r: 4 }}
                      activeDot={{ r: 6 }}
                    />
                    <Line
                      type="monotone"
                      dataKey="y"
                      name="Y Position"
                      stroke="#fb923c"
                      strokeWidth={2}
                      dot={{ fill: "#fb923c", r: 4 }}
                      activeDot={{ r: 6 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-100 d-flex align-items-center justify-content-center bg-light rounded">
                  <p className="text-muted small mb-0">
                    Click a result to view its position data
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PositionCharts;

<style jsx>{`
  .glass-card {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 12px;
  }
`}</style>;
