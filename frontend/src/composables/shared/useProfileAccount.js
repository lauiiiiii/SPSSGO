import { computed, reactive, ref } from 'vue'
import { changePassword as changePasswordRequest, changeUsername, getUsername } from '../../api.js'

export function useProfileAccount() {
  const username = ref(getUsername())
  const avatarChar = computed(() => (username.value || 'U')[0].toUpperCase())
  const createdAt = ref(new Date().toLocaleDateString('zh-CN'))
  const lastLogin = ref(new Date().toLocaleString('zh-CN'))

  const editingName = ref(false)
  const editName = ref('')
  const nameLoading = ref(false)
  const nameMsg = ref('')
  const nameOk = ref(false)

  const pwForm = reactive({ oldPwd: '', newPwd: '', confirmPwd: '' })
  const pwLoading = ref(false)
  const pwMsg = ref('')
  const pwOk = ref(false)

  function startEditingName() {
    editingName.value = true
    editName.value = username.value
    nameMsg.value = ''
  }

  function cancelEditingName() {
    editingName.value = false
    editName.value = ''
    nameMsg.value = ''
  }

  async function saveName() {
    nameMsg.value = ''
    const nextName = editName.value.trim()
    if (!nextName) {
      nameMsg.value = '用户名不能为空'
      nameOk.value = false
      return
    }
    if (nextName.length < 2) {
      nameMsg.value = '用户名至少2个字符'
      nameOk.value = false
      return
    }

    nameLoading.value = true
    try {
      const data = await changeUsername(nextName)
      if (data?.success) {
        localStorage.setItem('spssgo_user', nextName)
        username.value = nextName
        nameMsg.value = '用户名修改成功'
        nameOk.value = true
        editingName.value = false
      } else {
        nameMsg.value = data?.detail || data?.error || '修改失败'
        nameOk.value = false
      }
    } catch (error) {
      nameMsg.value = '请求失败：' + error.message
      nameOk.value = false
    }
    nameLoading.value = false
  }

  async function changePassword() {
    pwMsg.value = ''
    if (!pwForm.oldPwd) {
      pwMsg.value = '请输入当前密码'
      pwOk.value = false
      return
    }
    if (pwForm.newPwd.length < 6) {
      pwMsg.value = '新密码至少6位'
      pwOk.value = false
      return
    }
    if (pwForm.newPwd !== pwForm.confirmPwd) {
      pwMsg.value = '两次密码不一致'
      pwOk.value = false
      return
    }

    pwLoading.value = true
    try {
      const data = await changePasswordRequest(pwForm.oldPwd, pwForm.newPwd)
      if (data?.success) {
        pwMsg.value = '密码修改成功'
        pwOk.value = true
        pwForm.oldPwd = ''
        pwForm.newPwd = ''
        pwForm.confirmPwd = ''
      } else {
        pwMsg.value = data?.detail || data?.error || '修改失败'
        pwOk.value = false
      }
    } catch (error) {
      pwMsg.value = '请求失败：' + error.message
      pwOk.value = false
    }
    pwLoading.value = false
  }

  async function copyText(text) {
    try { await navigator.clipboard.writeText(text) } catch (_) {}
  }

  return {
    avatarChar,
    cancelEditingName,
    changePassword,
    copyText,
    createdAt,
    editingName,
    editName,
    lastLogin,
    nameLoading,
    nameMsg,
    nameOk,
    pwForm,
    pwLoading,
    pwMsg,
    pwOk,
    saveName,
    startEditingName,
    username,
  }
}
