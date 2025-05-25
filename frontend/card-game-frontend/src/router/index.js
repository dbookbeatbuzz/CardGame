import { createRouter, createWebHistory } from 'vue-router'
import Auth from '../views/Auth.vue'
import Dashboard from '../views/Dashboard.vue'
import Room from '../views/Room.vue'
import GameInterface from '../views/GameInterface.vue'
import GameRecords from '../views/GameRecords.vue'

const routes = [
  { path: '/', name: 'Auth', component: Auth },
  { path: '/dashboard', name: 'Dashboard', component: Dashboard },
  { path: '/room/:roomId', name: 'Room', component: Room, props: true },
  { path: '/game/:roomId', name: 'GameInterface', component: GameInterface, props: true },
  { path: '/records', name: 'GameRecords', component: GameRecords },
    {
  path: '/admin/users',
  name: 'AdminUserQuery',
  component: () => import('@/views/admin/UserQuery.vue')
},
{
  path: '/admin/rooms',
  name: 'AdminRoomManagement',
  component: () => import('@/views/admin/RoomManagement.vue')
},
{
  path: '/admin/records',
  name: 'AdminGameLogs',
  component: () => import('@/views/admin/GameLogs.vue')
}

]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router;
