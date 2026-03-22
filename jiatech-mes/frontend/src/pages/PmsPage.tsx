import { useEffect } from 'react';
import { Table, Card, Statistic, Row, Col, Tag, Button, Timeline, Space } from 'antd';
import { useSearch } from '@/hooks/useMesApi';
import type { MesModel } from '@/types/mes';

interface MaintenanceRequest extends MesModel {
  name: string;
  equipment_id: number;
  equipment_name?: string;
  type: 'corrective' | 'preventive' | 'predictive';
  priority: 'low' | 'medium' | 'high' | 'critical';
  state: 'draft' | 'confirmed' | 'in_progress' | 'done' | 'cancelled';
  request_date: string;
  done_date?: string;
  description?: string;
}

interface MaintenanceSchedule extends MesModel {
  name: string;
  equipment_id: number;
  period: number;
  period_unit: 'day' | 'week' | 'month' | 'year';
  next_date: string;
  active: boolean;
}

function PmsPage() {
  const { data: requests, search: searchRequests } = useSearch<MaintenanceRequest>('mes.maintenance.request');
  const { data: schedules, search: searchSchedules } = useSearch<MaintenanceSchedule>('mes.maintenance.schedule');

  useEffect(() => {
    searchRequests({ page: 1, pageSize: 10 });
    searchSchedules({ page: 1, pageSize: 10 });
  }, [searchRequests, searchSchedules]);

  const getPriorityColor = (p: string) => {
    switch (p) {
      case 'critical': return 'red';
      case 'high': return 'orange';
      case 'medium': return 'blue';
      case 'low': return 'green';
      default: return 'default';
    }
  };

  const getStateColor = (s: string) => {
    switch (s) {
      case 'draft': return 'default';
      case 'confirmed': return 'blue';
      case 'in_progress': return 'orange';
      case 'done': return 'green';
      case 'cancelled': return 'grey';
      default: return 'default';
    }
  };

  const getTypeColor = (t: string) => {
    switch (t) {
      case 'corrective': return 'red';
      case 'preventive': return 'blue';
      case 'predictive': return 'purple';
      default: return 'default';
    }
  };

  const requestColumns = [
    { title: 'Request', dataIndex: 'name', key: 'name' },
    { title: 'Equipment', dataIndex: 'equipment_name', key: 'equipment_name' },
    { title: 'Type', dataIndex: 'type', key: 'type', 
      render: (t: string) => <Tag color={getTypeColor(t)}>{t}</Tag> },
    { title: 'Priority', dataIndex: 'priority', key: 'priority',
      render: (p: string) => <Tag color={getPriorityColor(p)}>{p}</Tag> },
    { title: 'State', dataIndex: 'state', key: 'state',
      render: (s: string) => <Tag color={getStateColor(s)}>{s}</Tag> },
    { title: 'Request Date', dataIndex: 'request_date', key: 'request_date' },
  ];

  // Schedule columns for future table view
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const _scheduleColumns = [
    { title: 'Schedule', dataIndex: 'name', key: 'name' },
    { title: 'Equipment', dataIndex: 'equipment_id', key: 'equipment_id' },
    { title: 'Period', dataIndex: 'period', key: 'period', 
      render: (p: number, r: MaintenanceSchedule) => `${p} ${r.period_unit}(s)` },
    { title: 'Next Date', dataIndex: 'next_date', key: 'next_date' },
    { title: 'Status', key: 'status',
      render: (_: unknown, r: MaintenanceSchedule) => <Tag color={r.active ? 'green' : 'grey'}>{r.active ? 'Active' : 'Inactive'}</Tag> },
  ];

  const pendingCount = requests?.filter(r => r.state === 'draft' || r.state === 'confirmed').length || 0;
  const inProgressCount = requests?.filter(r => r.state === 'in_progress').length || 0;

  return (
    <div>
      <h2>Preventive Maintenance</h2>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card><Statistic title="Pending Requests" value={pendingCount} valueStyle={{ color: '#faad14' }} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="In Progress" value={inProgressCount} valueStyle={{ color: '#1890ff' }} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="Completed (MTD)" value={0} valueStyle={{ color: '#52c41a' }} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="Schedules" value={schedules?.length || 0} /></Card>
        </Col>
      </Row>
      <Row gutter={16}>
        <Col span={14}>
          <Card title="Maintenance Requests" extra={
            <Space>
              <Button type="primary">New Request</Button>
              <Button onClick={() => searchRequests({ page: 1, pageSize: 10 })}>Refresh</Button>
            </Space>
          }>
            <Table columns={requestColumns} dataSource={requests} rowKey="id" size="small" pagination={false} />
          </Card>
        </Col>
        <Col span={10}>
          <Card title="Upcoming Schedules">
            <Timeline
              items={schedules?.slice(0, 5).map(s => ({
                color: new Date(s.next_date) < new Date() ? 'red' : 'blue',
                children: `${s.name} - ${s.next_date}`,
              })) || []}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
}

export default PmsPage;
