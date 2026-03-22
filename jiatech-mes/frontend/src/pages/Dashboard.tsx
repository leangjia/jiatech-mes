import { Card, Row, Col, Statistic } from 'antd';

function Dashboard() {
  return (
    <div>
      <h2>Dashboard</h2>
      <Row gutter={16} style={{ marginTop: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic title="Active Lots" value={0} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="In Progress" value={0} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="Equipment Online" value={0} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="SPC Alarms" value={0} />
          </Card>
        </Col>
      </Row>
      <Row gutter={16} style={{ marginTop: 24 }}>
        <Col span={12}>
          <Card title="Recent Activity">
            <p>No recent activity</p>
          </Card>
        </Col>
        <Col span={12}>
          <Card title="System Status">
            <p>All systems operational</p>
          </Card>
        </Col>
      </Row>
    </div>
  );
}

export default Dashboard;
