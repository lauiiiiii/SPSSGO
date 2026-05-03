<template>
  <div class="pf-section">
    <h3 class="pf-section-title">关于系统</h3>
    <div class="pf-card">
      <div class="pf-about-row"><span class="pf-about-label">产品全称</span><span>Smart Processing Statistical System Guided Operations</span></div>
      <div class="pf-about-row"><span class="pf-about-label">产品简称</span><span>spssgo</span></div>
      <div class="pf-about-row"><span class="pf-about-label">系统版本</span><span>spssgo 3.0 数据分析工作台 社区版</span></div>
      <div class="pf-about-row"><span class="pf-about-label">产品介绍</span><span><a href="/about">查看关于我们页面</a></span></div>
      <div class="pf-about-row"><span class="pf-about-label">技术栈</span><span>Vue 3 + FastAPI + Pandas</span></div>
      <div class="pf-about-row"><span class="pf-about-label">支持格式</span><span>Excel / CSV / SPSS / Stata / SAS / Parquet</span></div>
      <div class="pf-about-row"><span class="pf-about-label">开源协议</span><span><a href="/legal#license">AGPL-3.0</a></span></div>
      <div class="pf-about-row"><span class="pf-about-label">版权归属</span><span>日照广泰佳和网络科技有限公司</span></div>
      <div class="pf-about-row"><span class="pf-about-label">公司邮箱</span><span class="pf-copyable" @click="$emit('copy', 'jahe@jahe.top')">jahe@jahe.top</span></div>
    </div>
    <h3 class="pf-section-title" style="margin-top:28px">授权说明</h3>
    <div class="pf-card">
      <div class="pf-license">
        <p>本系统基于 <strong>AGPL-3.0（GNU Affero General Public License v3.0）</strong> 开源协议发布。</p>
        <div class="pf-license-items">
          <div class="pf-license-item pf-license--free">
            <span class="pf-license-icon">✓</span>
            <div><strong>个人学习与研究</strong> — 免费使用，无需授权</div>
          </div>
          <div class="pf-license-item pf-license--free">
            <span class="pf-license-icon">✓</span>
            <div><strong>开源项目二次开发</strong> — 需保留原始版权声明，修改后的代码同样以 AGPL-3.0 发布</div>
          </div>
          <div class="pf-license-item pf-license--auth">
            <span class="pf-license-icon">⚠</span>
            <div><strong>商业用途</strong> — 需联系作者获取商业授权许可</div>
          </div>
          <div class="pf-license-item pf-license--auth">
            <span class="pf-license-icon">⚠</span>
            <div><strong>企业内部部署</strong> — 需联系作者获取企业授权许可</div>
          </div>
          <div class="pf-license-item pf-license--auth">
            <span class="pf-license-icon">⚠</span>
            <div><strong>学校 / 教育机构</strong> — 需联系作者获取教育授权许可</div>
          </div>
          <div class="pf-license-item pf-license--warn">
            <span class="pf-license-icon">✕</span>
            <div><strong>闭源分发</strong> — 不得将本系统或其修改版本以闭源形式分发</div>
          </div>
        </div>
        <p class="pf-license-note">如需商业授权或有任何疑问，请通过jahe@jahe.top与我们沟通</p>
      </div>
    </div>
    <h3 class="pf-section-title" style="margin-top:28px">联系我们</h3>
    <div class="pf-card">
      <div class="pf-about-row"><span class="pf-about-label">开发者QQ群</span><span class="pf-copyable" @click="$emit('copy', '978402915')">978402915</span></div>
    </div>
  </div>
</template>

<script setup>
defineEmits(['copy'])
</script>
