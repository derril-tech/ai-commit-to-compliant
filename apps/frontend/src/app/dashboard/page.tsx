'use client';

import { Container, Title, Grid, Card, Text, Button, Group, Badge, Stack } from '@mantine/core';
import { IconPlus, IconGitBranch, IconClock, IconCheck } from '@tabler/icons-react';
import { useAuth } from '@/lib/auth';
import { useProjects } from '@/lib/api';
import { AppShell } from '@/components/AppShell';

export default function DashboardPage() {
  const { user } = useAuth();
  const { projects, isLoading } = useProjects();

  if (!user) {
    return null; // Will redirect via auth guard
  }

  return (
    <AppShell>
      <Container size="xl">
        <Group justify="space-between" mb="xl">
          <div>
            <Title order={1}>Projects</Title>
            <Text c="dimmed">Manage your deployment pipelines</Text>
          </div>
          <Button leftSection={<IconPlus size={16} />}>
            Import Repository
          </Button>
        </Group>

        {isLoading ? (
          <Text>Loading projects...</Text>
        ) : projects?.length === 0 ? (
          <Card withBorder p="xl" ta="center">
            <Stack align="center" gap="md">
              <IconGitBranch size={48} color="gray" />
              <div>
                <Title order={3}>No projects yet</Title>
                <Text c="dimmed" mt="xs">
                  Import your first repository to get started
                </Text>
              </div>
              <Button leftSection={<IconPlus size={16} />}>
                Import Repository
              </Button>
            </Stack>
          </Card>
        ) : (
          <Grid>
            {projects?.map((project) => (
              <Grid.Col key={project.id} span={{ base: 12, md: 6, lg: 4 }}>
                <Card withBorder h="100%">
                  <Stack justify="space-between" h="100%">
                    <div>
                      <Group justify="space-between" mb="xs">
                        <Text fw={500} truncate>
                          {project.repo_url.split('/').pop()?.replace('.git', '')}
                        </Text>
                        <Badge 
                          color={project.state === 'ready' ? 'green' : 'yellow'}
                          variant="light"
                        >
                          {project.state}
                        </Badge>
                      </Group>
                      
                      <Text size="sm" c="dimmed" mb="md">
                        {project.repo_url}
                      </Text>
                      
                      <Group gap="xs" mb="md">
                        <IconGitBranch size={14} />
                        <Text size="sm">{project.branch}</Text>
                        <Text size="sm" c="dimmed">•</Text>
                        <Text size="sm">{project.target}</Text>
                      </Group>
                    </div>
                    
                    <Group justify="space-between">
                      <Group gap="xs">
                        <IconClock size={14} />
                        <Text size="xs" c="dimmed">
                          {new Date(project.updated_at).toLocaleDateString()}
                        </Text>
                      </Group>
                      <Button size="xs" variant="light">
                        View
                      </Button>
                    </Group>
                  </Stack>
                </Card>
              </Grid.Col>
            ))}
          </Grid>
        )}
      </Container>
    </AppShell>
  );
}
