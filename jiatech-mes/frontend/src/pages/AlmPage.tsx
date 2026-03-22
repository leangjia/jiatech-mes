import { useEffect } from 'react';
import { Table, Card, Statistic, Row, Col, Tag, Button, Space, Badge } from 'antd';
import { useSearch } from '@/hooks/useMesApi';
import type { MesModel } from '@/types/mes';

interface Alarm extends MesModel {
  name: string;
  code: string;
  alarm_type: 'info' | 'warning' | 'error' | 'critical';
  source: string;
  lot_id?: number;
  equipment_id?: number;
  state: 'active' | 'acknowledged' | 'resolved';
  priority: 1 | 2 | 3 | 4 | 5;
  message: string;
  create_date: string;
}

interface AlarmAction extends MesModel {
  alarm_id: number;
  action_type: 'notify' | 'email' | 'sms' | 'webhook' | 'stop_line';
  user_id?: number;
  state: 'pending' | 'done' | 'failed';
  done_date?: string;
}

function AlmPage() {
  const { data: alarms, search: searchAlarms } = useSearch<Alarm>('mes.alarm');
  const { data: actions, search: searchActions } = useSearch<AlarmAction>('mes.alarm.action');

  useEffect(() => {
    searchAlarms({ page: 1, pageSize: 15 });
    searchActions({ page: 1, pageSize: 10 });
  }, [searchAlarms, searchActions]);

  const getAlarmColor = (type: string) => {
    switch (type) {
      case 'critical': return 'red';
      case 'error': return 'orange';
      case 'warning': return 'gold';
      case 'info': return 'blue';
      default: return 'default';
    }
  };

  const getStateColor = (s: string) => {
    switch (s) {
      case 'active': return 'red';
      case 'acknowledged': return 'orange';
      case 'resolved': return 'green';
      default: return 'default';
    }
  };

  const activeAlarms = alarms?.filter(a => a.state === 'active').length || 0;
  const criticalAlarms = alarms?.filter(a => a.alarm_type === 'critical' && a.state === 'active').length || 0;

  const alarmColumns = [
    { title: 'Code', dataIndex: 'code', key: 'code', width: 100 },
    { title: 'Message', dataIndex: 'message', key: 'message', ellipsis: true },
    { title: 'Type', dataIndex: 'alarm_type', key: 'alarm_type',
      render: (t: string) => <Tag color={getAlarmColor(t)}>{t.toUpperCase()}</Tag> },
    { title: 'Source', dataIndex: 'source', key: 'source' },
    { title: 'Priority', dataIndex: 'priority', key: 'priority',
      render: (p: number) => <Badge count={p} showAsOverlay /> },
    { title: 'State', dataIndex: 'state', key: 'state',
      render: (s: string) => <Tag color={getStateColor(s)}>{s}</Tag> },
    { title: 'Time', dataIndex: 'create_date', key: 'create_date' },
  ];

  const actionColumns = [
    { title: 'Action Type', dataIndex: 'action_type', key: 'action_type',
      render: (t: string) => <Tag>{t}</Tag> },
    { title: 'Alarm', dataIndex: 'alarm_id', key: 'alarm_id' },
    { title: 'State', dataIndex: 'state', key: 'state',
      render: (s: string) => <Tag color={s === 'done' ? 'green' : s === 'failed' ? 'red' : 'orange'}>{s}</Tag> },
    { title: 'Date', dataIndex: 'done_date', key: 'done_date' },
  ];

  return (
    <div>
      <h2>Alarm Management</h2>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card><Statistic title="Active Alarms" value={activeAlarms} valueStyle={{ color: activeAlarms > 0 ? '#cf1322' : '#52c41a' }} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="Critical" value={criticalAlarms} valueStyle={{ color: criticalAlarms > 0 ? '#cf1322' : '#52c41a' }} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="Acknowledged" value={alarms?.filter(a => a.state === 'acknowledged').length || 0} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="Resolved (Today)" value={0} valueStyle={{ color: '#52c41a' }} /></Card>
        </Col>
      </Row>
      <Row gutter={16}>
        <Col span={14}>
          <Card title="Active Alarms" extra={
            <Space>
              <Button type="primary">Configure Rules</Button>
              <Button onClick={() => searchAlarms({ page: 1, pageSize: 15 })}>Refresh</Button>
            </Space>
          }>
            <Table columns={alarmColumns} dataSource={alarms} rowKey="id" size="small" pagination={false} />
          </Card>
        </Col>
        <Col span={10}>
          <Card title="Recent Actions">
            <Table columns={actionColumns} dataSource={actions} rowKey="id" size="small" pagination={false} />
          </Card>
        </Col>
      </Row>
    </div>
  );
}

export default AlmPage;
