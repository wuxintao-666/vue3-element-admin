import request from "@/utils/request";

const AUTH_BASE_URL = "/api/v1/auth";

const AuthAPI = {
  /** 登录接口*/
  login(data: LoginFormData) {
    const formData = new FormData();
    const payload = {
    username: data.username,
    password: data.password,
    captcha_key: data.captchaKey,
    captcha_code: data.captchaCode,
  };
  console.log(payload);
    return request<any, LoginResult>({
      url: `${AUTH_BASE_URL}/login`,
      method: "post",
      data: payload,
    });
  },

  /** 注册接口*/
  register(data: RegisterFormData) {
    const payload = {
      username: data.username,
      password: data.password,
      nickname: data.nickname,
      email: data.email,
      mobile: data.mobile,
      captcha_key: data.captchaKey,
      captcha_code: data.captchaCode,
    };
    return request<any, RegisterResult>({
      url: `${AUTH_BASE_URL}/register`,
      method: "post",
      data: payload,
    });
  },

  /** 刷新 token 接口*/
  refreshToken(refreshToken: string) {
    return request<any, LoginResult>({
      url: `${AUTH_BASE_URL}/refresh-token`,
      method: "post",
      params: { refreshToken },
      headers: {
        Authorization: "no-auth",
      },
    });
  },

  /** 退出登录接口 */
  logout() {
    return request({
      url: `${AUTH_BASE_URL}/logout`,
      method: "delete",
    });
  },

  /** 获取验证码接口*/
  getCaptcha() {
    return request<any, CaptchaInfo>({
      url: `${AUTH_BASE_URL}/captcha`,
      method: "get",
    });
  },
};

export default AuthAPI;

/** 登录表单数据 */
export interface LoginFormData {
  /** 用户名 */
  username: string;
  /** 密码 */
  password: string;
  /** 验证码缓存key */
  captchaKey: string;
  /** 验证码 */
  captchaCode: string;
  /** 记住我 */
  rememberMe: boolean;
}

/** 登录响应 */
export interface LoginResult {
  /** 访问令牌 */
  accessToken: string;
  /** 刷新令牌 */
  refreshToken: string;
  /** 令牌类型 */
  tokenType: string;
  /** 过期时间(秒) */
  expiresIn: number;
}

/** 验证码信息 */
export interface CaptchaInfo {
  /** 验证码缓存key */
  captchaKey: string;
  /** 验证码图片Base64字符串 */
  captchaBase64: string;
}

/** 注册表单数据 */
export interface RegisterFormData {
  /** 用户名 */
  username: string;
  /** 密码 */
  password: string;
  /** 邮箱 */
  email?: string;
  /** 手机号 */
  mobile?: string;
}

/** 注册响应 */
export interface RegisterResult {
  /** 用户ID */
  userId: number;
  /** 消息 */
  message: string;
}
