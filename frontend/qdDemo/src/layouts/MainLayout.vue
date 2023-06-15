<template>
  <q-layout view="lHh lpR fFf">
    <q-header reveal elevated class="bg-primary text-white">
      <q-toolbar>
        <q-btn dense flat round icon="menu" @click="toggleLeftDrawer" />

        <div class="q-pa-md q-gutter-sm">
          <q-breadcrumbs active-color="white">
            <q-breadcrumbs-el label="Home" />
            <q-breadcrumbs-el label="Components" />
            <q-breadcrumbs-el label="Breadcrumbs" />
          </q-breadcrumbs>
        </div>

        <q-toolbar-title></q-toolbar-title>

        <q-btn dense flat round icon="menu" @click="toggleRightDrawer" />
      </q-toolbar>
    </q-header>

    <q-drawer show-if-above v-model="leftDrawerOpen" side="left" elevated>
      <!-- drawer content -->

      <q-list>
        <template v-for="(menuItem, index) in menuList" :key="index">
          <q-item
            clickable
            v-ripple
            :to="menuItem.to"
            :active="link === 'outbox'"
          >
            <q-item-section avatar>
              <q-icon :name="menuItem.icon" />
            </q-item-section>
            <q-item-section>
              {{ menuItem.label }}
            </q-item-section>
          </q-item>
          <q-separator :key="'sep' + index" v-if="menuItem.separator" />
        </template>
      </q-list>
    </q-drawer>

    <q-drawer show-if-above v-model="rightDrawerOpen" side="right" bordered>
      <!-- drawer content -->
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref } from 'vue';

const menuList = ref([
  {
    icon: 'inbox',
    label: '继续阅读',
    separator: true,
    to: '/',
  },
  {
    icon: 'list',
    label: '小说列表',
    separator: false,
    to: '/BookList',
  },
  {
    icon: 'history',
    label: '阅读历史',
    separator: true,
    to: '/ReadHistory',
  },
  {
    icon: 'upload',
    label: '上传小说',
    separator: false,
    to: '/UserProfile',
  },
]);

const leftDrawerOpen = ref(false);
const rightDrawerOpen = ref(false);

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value;
}

function toggleRightDrawer() {
  rightDrawerOpen.value = !rightDrawerOpen.value;
}
</script>
