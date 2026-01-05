<template>
  <div class="empty-container">
    <el-empty
      :description="description"
      :image-size="imageSize"
      :image="image"
    >
      <slot></slot>
    </el-empty>
  </div>
</template>