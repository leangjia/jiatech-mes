import { useEffect } from 'react';
import { Table, Card, Statistic, Row, Col, Tag, Button } from 'antd';
import { useSearch } from '@/hooks/useMesApi';
import type { MesModel } from '@/types/mes';

interface SpcParameter extends MesModel {
  name: string;
  code: string;
  uom: string;
  upper_control_limit: number;
  lower_control_limit: number;
  upper_spec_limit: number;
  lower_spec_limit: number;
}

interface SpcAlarm extends MesModel {
  name?: string;
  parameter_id: number;
  alarm_type: 'ucl' | 'lcl' | 'usl' | 'lsl';
  lot_id: number;
  timestamp: string;
  value: number;
}

function SpcPage() {
  const { data: params, loading, search: searchParams } = useSearch<SpcParameter>('mes.spc.parameter');
  const { data: alarms, search: searchAlarms } = useSearch<SpcAlarm>('mes.spc.alarm');

  useEffect(() => {
    searchParams({ page: 1, pageSize: 10 });
    searchAlarms({ page: 1, pageSize: 5 });
  }, [searchParams, searchAlarms]);

  const getAlarmColor = (type: string) => {
    switch (type) {
      case 'ucl': return 'red';
      case 'lcl': return 'orange';
      case 'usl': return 'purple';
      case 'lsl': return 'blue';
      default: return 'default';
    }
  };

  const paramColumns = [
    { title: 'Code', dataIndex: 'code', key: 'code' },
    { title: 'Parameter', dataIndex: 'name', key: 'name' },
    { title: 'UOM', dataIndex: 'uom', key: 'uom' },
    { title: 'UCL', dataIndex: 'upper_control_limit', key: 'ucl' },
    { title: 'LCL', dataIndex: 'lower_control_limit', key: 'lcl' },
    { title: 'USL', dataIndex: 'upper_spec_limit', key: 'usl' },
    { title: 'LSL', dataIndex: 'lower_spec_limit', key: 'lsl' },
  ];

  const alarmColumns = [
    { title: 'Time', dataIndex: 'timestamp', key: 'timestamp' },
    { title: 'Lot', dataIndex: 'lot_id', key: 'lot_id' },
    { title: 'Type', dataIndex: 'alarm_type', key: 'alarm_type', 
      render: (t: string) => <Tag color={getAlarmColor(t)}>{t.toUpperCase()}</Tag> },
    { title: 'Value', dataIndex: 'value', key: 'value' },
  ];

  return (
    <div>
      <h2>Statistical Process Control</h2>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card><Statistic title="Total Parameters" value={0} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="Active Controls" value={0} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="Active Alarms" value={alarms?.length || 0} valueStyle={{ color: '#cf1322' }} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="Capability Index" value={0} suffix="σ" /></Card>
        </Col>
      </Row>
      <Row gutter={16}>
        <Col span={14}>
          <Card title="SPC Parameters" extra={<Button type="primary">Add Parameter</Button>}>
            <Table columns={paramColumns} dataSource={params} loading={loading} rowKey="id" size="small" pagination={false} />
          </Card>
        </Col>
        <Col span={10}>
          <Card title="Recent Alarms">
            <Table columns={alarmColumns} dataSource={alarms} rowKey="id" size="small" pagination={false} />
          </Card>
        </Col>
      </Row>
    </div>
  );
}

export default SpcPage;
