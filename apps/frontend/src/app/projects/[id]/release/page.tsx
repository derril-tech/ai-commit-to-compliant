'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import {
  Container,
  Title,
  Text,
  Card,
  Group,
  Badge,
  Button,
  Stack,
  Grid,
  Progress,
  Select,
  Switch,
  Alert,
  Timeline,
  ThemeIcon,
  Modal,
  Textarea,
} from '@mantine/core';
import {
  IconRocket,
  IconAlertTriangle,
  IconCheck,
  IconClock,
  IconX,
  IconPlayerPause,
  IconPlayerPlay,
  IconArrowBack,
  IconGitBranch,
  IconShield,
  IconGauge,
} from '@tabler/icons-react';
import { useDisclosure } from '@mantine/hooks';
import { notifications } from '@mantine/notifications';
import { AppShell } from '@/components/AppShell';
import { api } from '@/lib/api';

export default function ReleasePage() {
  const params = useParams();
  const projectId = params.id as string;
  const [strategy, setStrategy] = useState('blue-green');
  const [autoPromote, setAutoPromote] = useState(false);
  const [releasing, setReleasing] = useState(false);
  const [releaseStatus, setReleaseStatus] = useState<any>(null);
  const [rollbackModalOpened, { open: openRollbackModal, close: closeRollbackModal }] = useDisclosure(false);
  const [rollbackReason, setRollbackReason] = useState('');

  const strategies = [
    { value: 'blue-green', label: 'Blue-Green Deployment' },
    { value: 'canary', label: 'Canary Deployment' },
    { value: 'rolling', label: 'Rolling Deployment' },
    { value: 'direct', label: 'Direct Deployment' },
  ];

  const handleCreateRelease = async () => {
    try {
      setReleasing(true);
      const response = await api.post('/releases/create', {
        project_id: projectId,
        strategy,
        environment: 'production',
        auto_promote: autoPromote,
      });
      
      setReleaseStatus(response.data);
      
      notifications.show({
        title: 'Release Started',
        message: `${strategy} deployment has been initiated`,
        color: 'green',
      });

      // Poll for status updates
      pollReleaseStatus(response.data.release_id);
      
    } catch (error) {
      notifications.show({
        title: 'Error',
        message: 'Failed to start release',
        color: 'red',
      });
    } finally {
      setReleasing(false);
    }
  };

  const pollReleaseStatus = async (releaseId: string) => {
    try {
      const response = await api.get(`/releases/${releaseId}/status`);
      setReleaseStatus(response.data);
      
      // Continue polling if release is still running
      if (response.data.status === 'running') {
        setTimeout(() => pollReleaseStatus(releaseId), 5000);
      }
    } catch (error) {
      console.error('Failed to poll release status:', error);
    }
  };

  const handlePromoteRelease = async () => {
    if (!releaseStatus) return;
    
    try {
      await api.post(`/releases/${releaseStatus.release_id}/promote`);
      notifications.show({
        title: 'Release Promoted',
        message: 'Release has been promoted to full deployment',
        color: 'green',
      });
      pollReleaseStatus(releaseStatus.release_id);
    } catch (error) {
      notifications.show({
        title: 'Error',
        message: 'Failed to promote release',
        color: 'red',
      });
    }
  };

  const handlePauseRelease = async () => {
    if (!releaseStatus) return;
    
    try {
      await api.post(`/releases/${releaseStatus.release_id}/pause`);
      notifications.show({
        title: 'Release Paused',
        message: 'Release has been paused',
        color: 'blue',
      });
      pollReleaseStatus(releaseStatus.release_id);
    } catch (error) {
      notifications.show({
        title: 'Error',
        message: 'Failed to pause release',
        color: 'red',
      });
    }
  };

  const handleResumeRelease = async () => {
    if (!releaseStatus) return;
    
    try {
      await api.post(`/releases/${releaseStatus.release_id}/resume`);
      notifications.show({
        title: 'Release Resumed',
        message: 'Release has been resumed',
        color: 'green',
      });
      pollReleaseStatus(releaseStatus.release_id);
    } catch (error) {
      notifications.show({
        title: 'Error',
        message: 'Failed to resume release',
        color: 'red',
      });
    }
  };

  const handleRollback = async () => {
    if (!releaseStatus) return;
    
    try {
      await api.post('/releases/rollback', {
        release_id: releaseStatus.release_id,
        reason: rollbackReason || 'manual',
      });
      
      notifications.show({
        title: 'Rollback Initiated',
        message: 'Release rollback has been started',
        color: 'yellow',
      });
      
      closeRollbackModal();
      setRollbackReason('');
      
      // Refresh status
      pollReleaseStatus(releaseStatus.release_id);
      
    } catch (error) {
      notifications.show({
        title: 'Error',
        message: 'Failed to initiate rollback',
        color: 'red',
      });
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'green';
      case 'running': return 'blue';
      case 'failed': return 'red';
      case 'paused': return 'yellow';
      case 'rolled_back': return 'orange';
      default: return 'gray';
    }
  };

  const getPhaseIcon = (status: string) => {
    switch (status) {
      case 'completed': return <IconCheck size={16} />;
      case 'running': return <IconClock size={16} />;
      case 'failed': return <IconX size={16} />;
      default: return <IconClock size={16} />;
    }
  };

  const getStrategyDescription = (strategy: string) => {
    switch (strategy) {
      case 'blue-green':
        return 'Deploy to a parallel environment and switch traffic instantly';
      case 'canary':
        return 'Gradually roll out to a small percentage of users first';
      case 'rolling':
        return 'Update instances one by one with zero downtime';
      case 'direct':
        return 'Deploy directly to production (fastest but riskiest)';
      default:
        return '';
    }
  };

  const getRiskLevel = (strategy: string) => {
    switch (strategy) {
      case 'canary': return { level: 'LOW', color: 'green' };
      case 'blue-green': return { level: 'MEDIUM', color: 'yellow' };
      case 'rolling': return { level: 'MEDIUM', color: 'yellow' };
      case 'direct': return { level: 'HIGH', color: 'red' };
      default: return { level: 'MEDIUM', color: 'yellow' };
    }
  };

  const risk = getRiskLevel(strategy);

  return (
    <AppShell>
      <Container size="xl">
        <Group justify="space-between" mb="xl">
          <div>
            <Title order={1}>Release Management</Title>
            <Text c="dimmed">Deploy your application to production</Text>
          </div>
          <Button
            variant="outline"
            leftSection={<IconArrowBack size={16} />}
            onClick={() => window.history.back()}
          >
            Back to Readiness
          </Button>
        </Group>

        {!releaseStatus ? (
          // Release Configuration
          <Grid>
            <Grid.Col span={{ base: 12, md: 8 }}>
              <Card withBorder>
                <Title order={3} mb="md">Release Configuration</Title>
                
                <Stack gap="md">
                  <Select
                    label="Deployment Strategy"
                    description="Choose how you want to deploy your application"
                    data={strategies}
                    value={strategy}
                    onChange={(value) => setStrategy(value || 'blue-green')}
                  />
                  
                  <Text size="sm" c="dimmed">
                    {getStrategyDescription(strategy)}
                  </Text>
                  
                  <Switch
                    label="Auto-promote canary releases"
                    description="Automatically promote canary releases if health checks pass"
                    checked={autoPromote}
                    onChange={(event) => setAutoPromote(event.currentTarget.checked)}
                    disabled={strategy !== 'canary'}
                  />
                  
                  <Button
                    leftSection={<IconRocket size={16} />}
                    loading={releasing}
                    onClick={handleCreateRelease}
                    size="lg"
                  >
                    Start Release
                  </Button>
                </Stack>
              </Card>
            </Grid.Col>

            <Grid.Col span={{ base: 12, md: 4 }}>
              <Stack gap="md">
                <Card withBorder>
                  <Group gap="xs" mb="xs">
                    <ThemeIcon color={risk.color} variant="light" size="sm">
                      <IconShield size={16} />
                    </ThemeIcon>
                    <Text fw={500}>Risk Assessment</Text>
                  </Group>
                  <Badge color={risk.color} variant="light" mb="xs">
                    {risk.level} RISK
                  </Badge>
                  <Text size="sm" c="dimmed">
                    Based on deployment strategy and current conditions
                  </Text>
                </Card>

                <Card withBorder>
                  <Group gap="xs" mb="xs">
                    <ThemeIcon color="blue" variant="light" size="sm">
                      <IconGauge size={16} />
                    </ThemeIcon>
                    <Text fw={500}>Estimated Duration</Text>
                  </Group>
                  <Text fw={500}>
                    {strategy === 'canary' ? '45-60 min' : 
                     strategy === 'blue-green' ? '10-15 min' :
                     strategy === 'rolling' ? '15-20 min' : '5-10 min'}
                  </Text>
                  <Text size="sm" c="dimmed">
                    Including health checks and monitoring
                  </Text>
                </Card>
              </Stack>
            </Grid.Col>
          </Grid>
        ) : (
          // Release Status
          <Grid>
            <Grid.Col span={{ base: 12, md: 8 }}>
              <Card withBorder mb="md">
                <Group justify="space-between" mb="md">
                  <div>
                    <Group gap="xs" mb="xs">
                      <Title order={3}>Release Status</Title>
                      <Badge
                        color={getStatusColor(releaseStatus.status)}
                        variant="light"
                      >
                        {releaseStatus.status.toUpperCase()}
                      </Badge>
                    </Group>
                    <Text c="dimmed">
                      Release ID: {releaseStatus.release_id}
                    </Text>
                  </div>
                  <Group>
                    {releaseStatus.status === 'running' && strategy === 'canary' && (
                      <>
                        <Button
                          size="xs"
                          variant="outline"
                          leftSection={<IconPlayerPause size={14} />}
                          onClick={handlePauseRelease}
                        >
                          Pause
                        </Button>
                        <Button
                          size="xs"
                          onClick={handlePromoteRelease}
                        >
                          Promote
                        </Button>
                      </>
                    )}
                    {releaseStatus.status === 'paused' && (
                      <Button
                        size="xs"
                        leftSection={<IconPlayerPlay size={14} />}
                        onClick={handleResumeRelease}
                      >
                        Resume
                      </Button>
                    )}
                    {releaseStatus.rollback_available && (
                      <Button
                        size="xs"
                        variant="outline"
                        color="red"
                        leftSection={<IconArrowBack size={14} />}
                        onClick={openRollbackModal}
                      >
                        Rollback
                      </Button>
                    )}
                  </Group>
                </Group>

                <Progress
                  value={releaseStatus.progress_percentage || 0}
                  size="lg"
                  color={getStatusColor(releaseStatus.status)}
                  mb="md"
                />

                <Text size="sm" c="dimmed" mb="md">
                  Current Phase: {releaseStatus.current_phase?.replace('_', ' ')}
                </Text>

                {releaseStatus.traffic_split && (
                  <Group gap="md" mb="md">
                    <div>
                      <Text size="sm" fw={500}>Traffic Split</Text>
                      <Group gap="xs">
                        <Badge variant="light" color="blue">
                          Stable: {releaseStatus.traffic_split.stable}%
                        </Badge>
                        <Badge variant="light" color="green">
                          Canary: {releaseStatus.traffic_split.canary}%
                        </Badge>
                      </Group>
                    </div>
                  </Group>
                )}
              </Card>

              {/* Release Timeline */}
              <Card withBorder>
                <Title order={4} mb="md">Release Timeline</Title>
                <Timeline active={releaseStatus.phases?.findIndex((p: any) => p.status === 'running') || 0}>
                  {releaseStatus.phases?.map((phase: any, index: number) => (
                    <Timeline.Item
                      key={index}
                      bullet={getPhaseIcon(phase.status)}
                      title={phase.name?.replace('_', ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())}
                      color={getStatusColor(phase.status)}
                    >
                      <Text size="sm" c="dimmed">
                        {phase.status === 'completed' && phase.completed_at && (
                          <>Completed at {new Date(phase.completed_at).toLocaleTimeString()}</>
                        )}
                        {phase.status === 'running' && (
                          <>In progress... {Math.round(phase.progress_percentage || 0)}%</>
                        )}
                        {phase.status === 'pending' && phase.estimated_duration_minutes && (
                          <>Estimated duration: {phase.estimated_duration_minutes} minutes</>
                        )}
                        {phase.traffic_percentage && (
                          <> • Traffic: {phase.traffic_percentage}%</>
                        )}
                      </Text>
                    </Timeline.Item>
                  ))}
                </Timeline>
              </Card>
            </Grid.Col>

            <Grid.Col span={{ base: 12, md: 4 }}>
              <Stack gap="md">
                {/* Health Metrics */}
                <Card withBorder>
                  <Title order={4} mb="md">Health Metrics</Title>
                  <Stack gap="xs">
                    <Group justify="space-between">
                      <Text size="sm">Error Rate</Text>
                      <Text size="sm" fw={500}>
                        {releaseStatus.health_metrics?.error_rate || 0}%
                      </Text>
                    </Group>
                    <Group justify="space-between">
                      <Text size="sm">P95 Latency</Text>
                      <Text size="sm" fw={500}>
                        {releaseStatus.health_metrics?.p95_latency_ms || 0}ms
                      </Text>
                    </Group>
                    <Group justify="space-between">
                      <Text size="sm">Requests/min</Text>
                      <Text size="sm" fw={500}>
                        {releaseStatus.health_metrics?.requests_per_minute || 0}
                      </Text>
                    </Group>
                    <Group justify="space-between">
                      <Text size="sm">Success Rate</Text>
                      <Text size="sm" fw={500}>
                        {releaseStatus.health_metrics?.success_rate || 0}%
                      </Text>
                    </Group>
                  </Stack>
                </Card>

                {/* Release Info */}
                <Card withBorder>
                  <Title order={4} mb="md">Release Info</Title>
                  <Stack gap="xs">
                    <Group justify="space-between">
                      <Text size="sm">Strategy</Text>
                      <Badge variant="light">{strategy}</Badge>
                    </Group>
                    <Group justify="space-between">
                      <Text size="sm">Environment</Text>
                      <Badge variant="light" color="blue">Production</Badge>
                    </Group>
                    <Group justify="space-between">
                      <Text size="sm">Started</Text>
                      <Text size="sm">
                        {new Date(releaseStatus.updated_at).toLocaleTimeString()}
                      </Text>
                    </Group>
                  </Stack>
                </Card>
              </Stack>
            </Grid.Col>
          </Grid>
        )}

        {/* Rollback Modal */}
        <Modal
          opened={rollbackModalOpened}
          onClose={closeRollbackModal}
          title="Rollback Release"
        >
          <Stack gap="md">
            <Alert icon={<IconAlertTriangle size={16} />} color="yellow">
              This will rollback the current release to the previous stable version.
              This action cannot be undone.
            </Alert>
            
            <Textarea
              label="Rollback Reason (Optional)"
              placeholder="Explain why you're rolling back this release..."
              value={rollbackReason}
              onChange={(e) => setRollbackReason(e.target.value)}
              minRows={3}
            />
            
            <Group justify="flex-end">
              <Button variant="outline" onClick={closeRollbackModal}>
                Cancel
              </Button>
              <Button
                color="red"
                onClick={handleRollback}
              >
                Confirm Rollback
              </Button>
            </Group>
          </Stack>
        </Modal>
      </Container>
    </AppShell>
  );
}
