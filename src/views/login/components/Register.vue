<template>
  <div>
    <h3 text-center m-0 mb-20px>{{ t("login.reg") }}</h3>
    <el-form ref="formRef" :model="model" :rules="rules" size="large">
      <!-- 用户名 -->
      <el-form-item prop="username">
        <el-input v-model.trim="model.username" :placeholder="t('login.username')">
          <template #prefix>
            <el-icon><User /></el-icon>
          </template>
        </el-input>
      </el-form-item>

      <!-- 邮箱 -->
      <el-form-item prop="email">
        <el-input v-model.trim="model.email" :placeholder="t('login.email') || '邮箱'" type="email">
          <template #prefix>
            <el-icon><Message /></el-icon>
          </template>
        </el-input>
      </el-form-item>

      <!-- 手机号 -->
      <el-form-item prop="mobile">
        <el-input v-model.trim="model.mobile" :placeholder="t('login.mobile') || '手机号'">
          <template #prefix>
            <el-icon><Phone /></el-icon>
          </template>
        </el-input>
      </el-form-item>

      <!-- 密码 -->
      <el-tooltip :visible="isCapsLock" :content="t('login.capsLock')" placement="right">
        <el-form-item prop="password">
          <el-input
            v-model.trim="model.password"
            :placeholder="t('login.password')"
            type="password"
            show-password
            @keyup="checkCapsLock"
            @keyup.enter="submit"
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
      </el-tooltip>

      <el-tooltip :visible="isCapsLock" :content="t('login.capsLock')" placement="right">
        <el-form-item prop="confirmPassword">
          <el-input
            v-model.trim="model.confirmPassword"
            :placeholder="t('login.message.password.confirm')"
            type="password"
            show-password
            @keyup="checkCapsLock"
            @keyup.enter="submit"
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
      </el-tooltip>


      <el-form-item>
        <div class="flex-y-center w-full gap-10px">
          <el-checkbox v-model="isRead">{{ t("login.agree") }}</el-checkbox>
          <el-link type="primary" underline="never">{{ t("login.userAgreement") }}</el-link>
        </div>
      </el-form-item>

      <!-- 注册按钮 -->
      <el-form-item>
        <el-button :loading="loading" type="success" class="w-full" @click="submit">
          {{ t("login.register") }}
        </el-button>
      </el-form-item>
    </el-form>
    <div flex-center gap-10px>
      <el-text size="default">{{ t("login.haveAccount") }}</el-text>
      <el-link type="primary" underline="never" @click="toLogin">{{ t("login.login") }}</el-link>
    </div>
  </div>
</template>
<script setup lang="ts">
import type { FormInstance } from "element-plus";
import { Lock, Message, Phone } from "@element-plus/icons-vue";
import { useI18n } from "vue-i18n";
import AuthAPI, { type RegisterFormData } from "@/api/auth-api";

const { t } = useI18n();

const emit = defineEmits(["update:modelValue"]);
const toLogin = () => emit("update:modelValue", "login");


const formRef = ref<FormInstance>();
const loading = ref(false); // 按钮 loading 状态
const isCapsLock = ref(false); // 是否大写锁定
const isRead = ref(false);

interface Model extends RegisterFormData {
  confirmPassword: string;
}

const model = ref<Model>({
  username: "",
  password: "",
  confirmPassword: "",
  email: "",
  mobile: "",
});

const rules = computed(() => {
  return {
    username: [
      {
        required: true,
        trigger: "blur",
        message: t("login.message.username.required"),
      },
      {
        min: 3,
        max: 20,
        message: "用户名长度应为3-20个字符",
        trigger: "blur",
      },
    ],
    email: [
      {
        type: "email",
        message: "请输入正确的邮箱格式",
        trigger: "blur",
      },
    ],
    mobile: [
      {
        pattern: /^1[3-9]\d{9}$/,
        message: "请输入正确的手机号",
        trigger: "blur",
      },
    ],
    password: [
      {
        required: true,
        trigger: "blur",
        message: t("login.message.password.required"),
      },
      {
        min: 6,
        message: t("login.message.password.min"),
        trigger: "blur",
      },
    ],
    confirmPassword: [
      {
        required: true,
        trigger: "blur",
        message: t("login.message.password.required"),
      },
      {
        min: 6,
        message: t("login.message.password.min"),
        trigger: "blur",
      },
      {
        validator: (_: any, value: string) => {
          return value === model.value.password;
        },
        trigger: "blur",
        message: t("login.message.password.inconformity"),
      },
    ],
  };
});


// 检查输入大小写
function checkCapsLock(event: KeyboardEvent) {
  // 防止浏览器密码自动填充时报错
  if (event instanceof KeyboardEvent) {
    isCapsLock.value = event.getModifierState("CapsLock");
  }
}

const submit = async () => {
  await formRef.value?.validate();

  if (!isRead.value) {
    ElMessage.warning("请先同意用户协议");
    return;
  }

  loading.value = true;

  try {
    const registerData: RegisterFormData = {
      username: model.value.username,
      password: model.value.password,
      email: model.value.email,
      mobile: model.value.mobile,
    };

    await AuthAPI.register(registerData);

    ElMessage.success("注册成功！请登录");
    // 切换到登录页面
    toLogin();
  } catch (error: any) {
    console.error("注册失败:", error);
    ElMessage.error(error?.message || "注册失败，请重试");
  } finally {
    loading.value = false;
  }
};
</script>
