import { defineMock } from "./base";

export default defineMock([
  {
    url: "users/me",
    method: ["GET"],
    body: {
      code: "00000",
      data: {
        userId: 2,
        username: "admin",
        nickname: "系统管理员",
        avatar: "https://foruda.gitee.com/images/1723603502796844527/03cdca2a_716974.gif",
        roles: ["ADMIN"],
        perms: [
          "sys:user:query",
          "sys:user:add",
          "sys:user:edit",
          "sys:user:delete",
          "sys:user:import",
          "sys:user:export",
          "sys:user:reset-password",

          "sys:role:query",
          "sys:role:add",
          "sys:role:edit",
          "sys:role:delete",

          "sys:dept:query",
          "sys:dept:add",
          "sys:dept:edit",
          "sys:dept:delete",

          "sys:menu:query",
          "sys:menu:add",
          "sys:menu:edit",
          "sys:menu:delete",

          "sys:dict:query",
          "sys:dict:add",
          "sys:dict:edit",
          "sys:dict:delete",
          "sys:dict:delete",

          "sys:dict-item:query",
          "sys:dict-item:add",
          "sys:dict-item:edit",
          "sys:dict-item:delete",

          "sys:notice:query",
          "sys:notice:add",
          "sys:notice:edit",
          "sys:notice:delete",
          "sys:notice:revoke",
          "sys:notice:publish",

          "sys:config:query",
          "sys:config:add",
          "sys:config:update",
          "sys:config:delete",
          "sys:config:refresh",
        ],
      },
      msg: "一切ok",
    },
  },

  {
    url: "users/page",
    method: ["GET"],
    body: {
      code: "00000",
      data: {
        list: [
          {
            id: 1,
            username: "user1",
            nickname: "系统管理员",
            mobile: "17621210366",
            gender: 1,
            avatar: "https://foruda.gitee.com/images/1723603502796844527/03cdca2a_716974.gif",
            email: "123456@163.com",
            status: 1,
            deptId: 1,
            roleIds: [2],
            password: "123456",
            createtime: "2023-01-01 12:00:00",
            recentsignin: "2023-02-01 12:00:00",
          },
          {
            id: 2,
            username: "user2",
            nickname: "测试小用户",
            mobile: "17621210123",
            gender: 1,
            avatar: "https://foruda.gitee.com/images/1723603502796844527/03cdca2a_716974.gif",
            email: "123456@163.com",
            status: 0,
            deptId: 3,
            roleIds: [3],
            password: "123456",
            createtime: "2023-02-01 12:00:00",
            recentsignin: "2023-02-01 12:00:00",
          },
          {
          id: 3,
          username: "user3",
          nickname: "普通用户A",
          mobile: "17621210003",
          gender: 2,
          avatar: "https://foruda.gitee.com/images/1723603502796844527/03cdca2a_716974.gif",
          email: "user3@163.com",
          status: 1,
          deptId: 2,
          roleIds: [4],
          password: "123456",
          createtime: "2023-03-01 09:30:00",
          recentsignin: "2023-03-05 10:00:00",
        },
        {
          id: 4,
          username: "user4",
          nickname: "普通用户B",
          mobile: "17621210004",
          gender: 1,
          avatar: "https://foruda.gitee.com/images/1723603502796844527/03cdca2a_716974.gif",
          email: "user4@163.com",
          status: 1,
          deptId: 2,
          roleIds: [4],
          password: "123456",
          createtime: "2023-03-02 11:20:00",
          recentsignin: "2023-03-06 08:45:00",
        },
        {
          id: 5,
          username: "user5",
          nickname: "产品经理",
          mobile: "17621210005",
          gender: 2,
          avatar: "https://foruda.gitee.com/images/1723603502796844527/03cdca2a_716974.gif",
          email: "user5@163.com",
          status: 1,
          deptId: 4,
          roleIds: [5],
          password: "123456",
          createtime: "2023-03-05 14:10:00",
          recentsignin: "2023-03-10 16:30:00",
        },
        {
          id: 6,
          username: "user6",
          nickname: "前端工程师",
          mobile: "17621210006",
          gender: 1,
          avatar: "https://foruda.gitee.com/images/1723603502796844527/03cdca2a_716974.gif",
          email: "user6@163.com",
          status: 1,
          deptId: 5,
          roleIds: [6],
          password: "123456",
          createtime: "2023-03-08 10:00:00",
          recentsignin: "2023-03-12 09:20:00",
        },
        {
          id: 7,
          username: "user7",
          nickname: "后端工程师",
          mobile: "17621210007",
          gender: 1,
          avatar: "https://foruda.gitee.com/images/1723603502796844527/03cdca2a_716974.gif",
          email: "user7@163.com",
          status: 1,
          deptId: 5,
          roleIds: [6],
          password: "123456",
          createtime: "2023-03-10 15:40:00",
          recentsignin: "2023-03-15 11:10:00",
        },
        {
          id: 8,
          username: "user8",
          nickname: "测试工程师",
          mobile: "17621210008",
          gender: 2,
          avatar: "https://foruda.gitee.com/images/1723603502796844527/03cdca2a_716974.gif",
          email: "user8@163.com",
          status: 0,
          deptId: 6,
          roleIds: [7],
          password: "123456",
          createtime: "2023-03-12 13:25:00",
          recentsignin: "2023-03-18 17:00:00",
        },
        {
          id: 9,
          username: "user9",
          nickname: "运维工程师",
          mobile: "17621210009",
          gender: 1,
          avatar: "https://foruda.gitee.com/images/1723603502796844527/03cdca2a_716974.gif",
          email: "user9@163.com",
          status: 1,
          deptId: 7,
          roleIds: [8],
          password: "123456",
          createtime: "2023-03-15 09:00:00",
          recentsignin: "2023-03-20 09:30:00",
        },
        {
          id: 10,
          username: "user10",
          nickname: "数据分析师",
          mobile: "17621210010",
          gender: 2,
          avatar: "https://foruda.gitee.com/images/1723603502796844527/03cdca2a_716974.gif",
          email: "user10@163.com",
          status: 1,
          deptId: 8,
          roleIds: [9],
          password: "123456",
          createtime: "2023-03-18 16:45:00",
          recentsignin: "2023-03-22 10:15:00",
        },
        {
          id: 11,
          username: "user11",
          nickname: "人事专员",
          mobile: "17621210011",
          gender: 2,
          avatar: "https://foruda.gitee.com/images/1723603502796844527/03cdca2a_716974.gif",
          email: "user11@163.com",
          status: 1,
          deptId: 9,
          roleIds: [10],
          password: "123456",
          createtime: "2023-03-20 08:50:00",
          recentsignin: "2023-03-25 14:00:00",
        },
        {
          id: 12,
          username: "user12",
          nickname: "财务人员",
          mobile: "17621210012",
          gender: 1,
          avatar: "https://foruda.gitee.com/images/1723603502796844527/03cdca2a_716974.gif",
          email: "user12@163.com",
          status: 0,
          deptId: 10,
          roleIds: [11],
          password: "123456",
          createtime: "2023-03-22 10:30:00",
          recentsignin: "2023-03-28 16:40:00",
        },
        ],
        total: 2,
      },
      msg: "一切ok",
    },
  },

  // 新增用户
  {
    url: "users",
    method: ["POST"],
    body({ body }) {
      return {
        code: "00000",
        data: null,
        msg: "新增用户" + body.nickname + "成功",
      };
    },
  },

  // 获取用户表单数据
  {
    url: "users/:userId/form",
    method: ["GET"],
    body: ({ params }) => {
      return {
        code: "00000",
        data: userMap[params.userId],
        msg: "一切ok",
      };
    },
  },
  // 修改用户
  {
    url: "users/:userId",
    method: ["PUT"],
    body({ body }) {
      return {
        code: "00000",
        data: null,
        msg: "修改用户" + body.nickname + "成功",
      };
    },
  },

  // 删除用户
  {
    url: "users/:userId",
    method: ["DELETE"],
    body({ params }) {
      return {
        code: "00000",
        data: null,
        msg: "删除用户" + params.id + "成功",
      };
    },
  },

  // 重置密码
  {
    url: "users/:userId/password/reset",
    method: ["PUT"],
    body({ query }) {
      return {
        code: "00000",
        data: null,
        msg: "重置密码成功，新密码为：" + query.password,
      };
    },
  },

  // 导出Excel
  {
    url: "users/_export",
    method: ["GET"],
    headers: {
      "Content-Disposition": "attachment; filename=%E7%94%A8%E6%88%B7%E5%88%97%E8%A1%A8.xlsx",
      "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    },
  },

  {
    url: "users/profile",
    method: ["GET"],
    body: {
      code: "00000",
      data: {
        id: 2,
        username: "admin",
        nickname: "系统管理员",
        avatar: "https://foruda.gitee.com/images/1723603502796844527/03cdca2a_716974.gif",
        gender: 1,
        mobile: "17621210366",
        email: null,
        deptName: "有来技术",
        roleNames: "系统管理员",
        createTime: "2019-10-10",
      },
    },
  },

  {
    url: "users/profile",
    method: ["PUT"],
    body() {
      return {
        code: "00000",
        data: null,
        msg: "修改个人信息成功",
      };
    },
  },

  {
    url: "users/password",
    method: ["PUT"],
    body() {
      return {
        code: "00000",
        data: null,
        msg: "修改密码成功",
      };
    },
  },
]);

// 用户映射表数据
const userMap: Record<string, any> = {
  2: {
    id: 2,
    username: "admin",
    nickname: "系统管理员",
    mobile: "17621210366",
    gender: 1,
    avatar: "https://foruda.gitee.com/images/1723603502796844527/03cdca2a_716974.gif",
    email: "",
    status: 1,
    deptId: 1,
    roleIds: [2],
  },
  3: {
    id: 3,
    username: "test",
    nickname: "测试小用户",
    mobile: "17621210366",
    gender: 1,
    avatar: "https://foruda.gitee.com/images/1723603502796844527/03cdca2a_716974.gif",
    email: "youlaitech@163.com",
    status: 1,
    deptId: 3,
    roleIds: [3],
  },
};
