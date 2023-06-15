<template>
  <q-page class="row items-start justify-evenly">
    <div class="q-pa-md col-12">
      <q-list>
        <template v-for="book in booklist" :key="book.bookid">
          <q-item>
            <q-item-section clickable>
              <q-item-label lines="1">{{ book.title }}</q-item-label>
              <q-item-label caption lines="3"
                >作者：{{ book.author }}<br />简介：{{
                  book.description
                }}</q-item-label
              >
            </q-item-section>

            <q-item-section side top>
              <q-item-label caption>上次读到</q-item-label>
              <q-item-label caption></q-item-label>
            </q-item-section>
          </q-item>

          <q-separator spaced inset />
        </template>
      </q-list>
    </div>
  </q-page>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';

axios
  .get('/books')
  .then(function (response) {
    console.log(response);
    booklist.value = response.data.books;
  })
  .catch(function (error) {
    console.log(error);
  })
  .finally(function () {
    console.log('finished');
  });

const booklist = ref([]);
</script>
