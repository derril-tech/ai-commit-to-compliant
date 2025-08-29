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
  List,
  ThemeIcon,
  ActionIcon,
  Tooltip,
  Modal,
  Textarea,
  Alert,
  Tabs,
} from '@mantine/core';
import {
  IconCheck,
  IconX,
  IconAlertTriangle,
  IconInfoCircle,
  IconExternalLink,
  IconRefresh,
  IconRocket,
  IconShield,
  IconGauge,
  IconSettings,
  IconEye,
} from '@tabler/icons-react';
import { useDisclosure } from '@mantine/hooks';
import { notifications } from '@mantine/notifications';
import { AppShell } from '@/components/AppShell';
import { useReadiness, api } from '@/lib/api';

export default function ReadinessPage() {
  const params = useParams();
  const projectId = params.id as string;
  const { readiness, isLoading, mutate } = useReadiness(projectId);
  const [refreshing, setRefreshing] = useState(false);
  const [waiveModalOpened, { open: openWaiveModal, close: closeWaiveModal }] = useDisclosure(false);
  const [selectedCheck, setSelectedCheck] = useState<any>(null);
  const [waiveReason, setWaiveReason] = useState('');

  if (isLoading) {
    return (
      <AppShell>
        <Container size="xl">
          <Text>Loading readiness checks...</Text>
        </Container>
      </AppShell>
    );
  }

  if (!readiness) {
    return (
      <AppShell>
        <Container size="xl">
          <Alert icon={<IconAlertTriangle size={16} />} color="yellow">
            No readiness data available. Please run the readiness checks first.
          </Alert>
        </Container>
      </AppShell>
    );
  }

  const handleRefresh = async () => {
    try {
      setRefreshing(true);
      await mutate();
      notifications.show({
        title: 'Refreshed',
        message: 'Readiness checks have been refreshed',
        color: 'blue',
      });
    } catch (error) {
      notifications.show({
        title: 'Error',
        message: 'Failed to refresh readiness checks',
        color: 'red',
      });
    } finally {
      setRefreshing(false);
    }
  };

  const handleWaiveCheck = async () => {
    try {
      await api.post(`/runs/readiness/${projectId}/waive`, {
        check_name: selectedCheck.name,
        reason: waiveReason,
      });
      notifications.show({
        title: 'Check Waived',
        message: `${selectedCheck.name} has been waived`,
        color: 'blue',
      });
      closeWaiveModal();
      setWaiveReason('');
      mutate();
    } catch (error) {
      notifications.show({
        title: 'Error',
        message: 'Failed to waive check',
        color: 'red',
      });
    }
  };

  const handleProceedToRelease = () => {
    window.location.href = `/projects/${projectId}/release`;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'passed': return 'green';
      case 'failed': return 'red';
      case 'waived': return 'yellow';
      case 'pending': return 'gray';
      default: return 'gray';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'passed': return <IconCheck size={16} />;
      case 'failed': return <IconX size={16} />;
      case 'waived': return <IconAlertTriangle size={16} />;
      default: return <IconInfoCircle size={16} />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'red';
      case 'medium': return 'yellow';
      case 'low': return 'blue';
      default: return 'gray';
    }
  };

  const categorizeChecks = (checks: any[]) => {
    const categories: { [key: string]: any[] } = {};
    checks.forEach(check => {
      const category = check.category || 'other';
      if (!categories[category]) {
        categories[category] = [];
      }
      categories[category].push(check);
    });
    return categories;
  };

  const categorizedChecks = categorizeChecks(readiness.checks);
  const canProceed = readiness.overall_status === 'ready' || readiness.blockers.length === 0;

  return (
    <AppShell>
      <Container size="xl">
        <Group justify="space-between" mb="xl">
          <div>
            <Title order={1}>Deployment Readiness</Title>
            <Text c="dimmed">Review readiness gates before deployment</Text>
          </div>
          <Group>
            <Button
              variant="outline"
              leftSection={<IconRefresh size={16} />}
              loading={refreshing}
              onClick={handleRefresh}
            >
              Refresh
            </Button>
            <Button
              leftSection={<IconRocket size={16} />}
              disabled={!canProceed}
              onClick={handleProceedToRelease}
            >
              Proceed to Release
            </Button>
          </Group>
        </Group>

        {/* Overall Status */}
        <Card withBorder mb="xl">
          <Group justify="space-between" mb="md">
            <div>
              <Group gap="xs" mb="xs">
                <Title order={3}>Overall Status</Title>
                <Badge
                  color={getStatusColor(readiness.overall_status)}
                  variant="light"
                  size="lg"
                >
                  {readiness.overall_status.toUpperCase()}
                </Badge>
              </Group>
              <Text c="dimmed">
                Last updated: {new Date(readiness.updated_at).toLocaleString()}
              </Text>
            </div>
            <div style={{ textAlign: 'right' }}>
              <Text size="xl" fw={700}>
                {Math.round(readiness.overall_score || 0)}%
              </Text>
              <Text size="sm" c="dimmed">Readiness Score</Text>
            </div>
          </Group>

          <Progress
            value={readiness.overall_score || 0}
            size="lg"
            color={readiness.overall_score >= 80 ? 'green' : readiness.overall_score >= 60 ? 'yellow' : 'red'}
            mb="md"
          />

          {readiness.blockers && readiness.blockers.length > 0 && (
            <Alert icon={<IconAlertTriangle size={16} />} color="red" mb="md">
              <Text fw={500}>Deployment Blocked</Text>
              <List size="sm" mt="xs">
                {readiness.blockers.map((blocker: string, index: number) => (
                  <List.Item key={index}>{blocker}</List.Item>
                ))}
              </List>
            </Alert>
          )}
        </Card>

        {/* Readiness Checks by Category */}
        <Tabs defaultValue="all">
          <Tabs.List>
            <Tabs.Tab value="all" leftSection={<IconEye size={16} />}>
              All Checks ({readiness.checks.length})
            </Tabs.Tab>
            {Object.entries(categorizedChecks).map(([category, checks]) => {
              const icon = {
                security: <IconShield size={16} />,
                performance: <IconGauge size={16} />,
                quality: <IconCheck size={16} />,
                infrastructure: <IconSettings size={16} />,
              }[category] || <IconInfoCircle size={16} />;

              return (
                <Tabs.Tab key={category} value={category} leftSection={icon}>
                  {category.charAt(0).toUpperCase() + category.slice(1)} ({checks.length})
                </Tabs.Tab>
              );
            })}
          </Tabs.List>

          <Tabs.Panel value="all" pt="md">
            <Grid>
              {readiness.checks.map((check: any, index: number) => (
                <Grid.Col key={index} span={{ base: 12, md: 6, lg: 4 }}>
                  <Card withBorder h="100%">
                    <Stack justify="space-between" h="100%">
                      <div>
                        <Group justify="space-between" mb="xs">
                          <Group gap="xs">
                            <ThemeIcon
                              color={getStatusColor(check.status)}
                              variant="light"
                              size="sm"
                            >
                              {getStatusIcon(check.status)}
                            </ThemeIcon>
                            <Text fw={500} size="sm">{check.name}</Text>
                          </Group>
                          <Badge
                            color={getSeverityColor(check.severity)}
                            variant="light"
                            size="xs"
                          >
                            {check.severity}
                          </Badge>
                        </Group>

                        <Text size="sm" c="dimmed" mb="md">
                          {check.message}
                        </Text>

                        <Badge variant="light" size="xs" mb="md">
                          {check.category}
                        </Badge>
                      </div>

                      <Group justify="space-between">
                        <Group gap="xs">
                          {check.remediation_url && (
                            <Tooltip label="View documentation">
                              <ActionIcon
                                variant="subtle"
                                size="sm"
                                onClick={() => window.open(check.remediation_url, '_blank')}
                              >
                                <IconExternalLink size={14} />
                              </ActionIcon>
                            </Tooltip>
                          )}
                        </Group>
                        {check.status === 'failed' && check.waivable && (
                          <Button
                            size="xs"
                            variant="outline"
                            onClick={() => {
                              setSelectedCheck(check);
                              openWaiveModal();
                            }}
                          >
                            Waive
                          </Button>
                        )}
                      </Group>
                    </Stack>
                  </Card>
                </Grid.Col>
              ))}
            </Grid>
          </Tabs.Panel>

          {Object.entries(categorizedChecks).map(([category, checks]) => (
            <Tabs.Panel key={category} value={category} pt="md">
              <Grid>
                {checks.map((check: any, index: number) => (
                  <Grid.Col key={index} span={{ base: 12, md: 6, lg: 4 }}>
                    <Card withBorder h="100%">
                      <Stack justify="space-between" h="100%">
                        <div>
                          <Group justify="space-between" mb="xs">
                            <Group gap="xs">
                              <ThemeIcon
                                color={getStatusColor(check.status)}
                                variant="light"
                                size="sm"
                              >
                                {getStatusIcon(check.status)}
                              </ThemeIcon>
                              <Text fw={500} size="sm">{check.name}</Text>
                            </Group>
                            <Badge
                              color={getSeverityColor(check.severity)}
                              variant="light"
                              size="xs"
                            >
                              {check.severity}
                            </Badge>
                          </Group>

                          <Text size="sm" c="dimmed" mb="md">
                            {check.message}
                          </Text>
                        </div>

                        <Group justify="space-between">
                          <Group gap="xs">
                            {check.remediation_url && (
                              <Tooltip label="View documentation">
                                <ActionIcon
                                  variant="subtle"
                                  size="sm"
                                  onClick={() => window.open(check.remediation_url, '_blank')}
                                >
                                  <IconExternalLink size={14} />
                                </ActionIcon>
                              </Tooltip>
                            )}
                          </Group>
                          {check.status === 'failed' && check.waivable && (
                            <Button
                              size="xs"
                              variant="outline"
                              onClick={() => {
                                setSelectedCheck(check);
                                openWaiveModal();
                              }}
                            >
                              Waive
                            </Button>
                          )}
                        </Group>
                      </Stack>
                    </Card>
                  </Grid.Col>
                ))}
              </Grid>
            </Tabs.Panel>
          ))}
        </Tabs>

        {/* Waive Check Modal */}
        <Modal
          opened={waiveModalOpened}
          onClose={closeWaiveModal}
          title={`Waive Check: ${selectedCheck?.name}`}
        >
          <Stack gap="md">
            <Text size="sm">
              Provide a reason for waiving this readiness check. This action will be logged for audit purposes.
            </Text>
            <Textarea
              label="Reason for waiving"
              placeholder="Explain why this check should be waived..."
              value={waiveReason}
              onChange={(e) => setWaiveReason(e.target.value)}
              minRows={3}
              required
            />
            <Group justify="flex-end">
              <Button variant="outline" onClick={closeWaiveModal}>
                Cancel
              </Button>
              <Button
                onClick={handleWaiveCheck}
                disabled={!waiveReason.trim()}
              >
                Waive Check
              </Button>
            </Group>
          </Stack>
        </Modal>
      </Container>
    </AppShell>
  );
}
