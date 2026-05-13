import React from "react";

interface SettingsSectionProps {
  title: string;
  description?: string;
  children: React.ReactNode;
}

export const SettingsSection: React.FC<SettingsSectionProps> = ({
  title,
  description,
  children,
}) => (
  <section className="py-10 first:pt-0 border-b border-border/60 last:border-0">
    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
      <div className="md:col-span-1">
        <h2 className="text-sm font-semibold text-primary uppercase tracking-wider">
          {title}
        </h2>
        {description && (
          <p className="text-sm text-muted-foreground mt-2 leading-relaxed">
            {description}
          </p>
        )}
      </div>
      <div className="md:col-span-2 space-y-6">{children}</div>
    </div>
  </section>
);
